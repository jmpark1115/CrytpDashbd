'''
옵션 프리미엄 비교
거래소 api 를 통한 데이터 수집
'''

import os, sys
import json, time
import threading
import random
from datetime import datetime, timedelta

from decimal import Decimal as D
from decimal import getcontext
getcontext().prec = 10

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse

try:
    # from exchange.binance     import Binance
    # from exchange.bybit       import Bybit
    # from exchange.debribit    import Debribit
    from exchange.okx         import Okx
except Exception as ex:
    raise ValueError(ex)

from .models import *

import logging
logger = logging.getLogger(__name__)

from concurrent.futures import ThreadPoolExecutor, as_completed

'''
    # def model_test(self):
    #     logger.debug('model_test')
    #     trading = Trading.objects.all().first()
    #     exs = trading.exchanger.all()
    #     for ex in exs:
    #         logger.debug(f'{ex.id}_{ex.name}')
    #     user = Username.objects.all()[1]
    #     tradings = user.trading_set.all()
    #     for tr in tradings:
    #         logger.debug(f'{tr.id}_{tr.name}')
    #     return

'''

class Handler(object):
    def __init__(self, bot):  # bot : specific Arbitrage
        self.id  = bot.id
        self.botname = f'{bot.id}_{bot.name}'

        self.hit = 0
        self.loop_number = 0

        self.t1 = None
        self.markets = list()   # markets : exchanger API
        self.arbitrage = None
        self.dryrun = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.optionsInfo = list()
        self.expireDateInfo = list()
        self.get_config()
        return

    def get_config(self):
        logger.debug(f'\nhandler get config_{self.botname}')
        self.arbitrage = Arbitrage.objects.get(id=self.id) #Arbitrage
        bots = self.arbitrage.arbibot.filter(enable=True) # ArbiBot
        # Exchanger API create
        self.markets = list()
        for b in bots:
            if b.exchanger == 'bybit':
                self.markets.append(Bybit(b.id))
            elif b.exchanger == 'binance':
                self.markets.append(Binance(b.id))
            elif b.exchanger == 'okx':
                self.markets.append(Okx(b.id))
            elif b.exchanger == 'debribit':
                self.markets.append(Debribit(b.id))
            else:
                logger.debug(f'Unsupported exchanger_{b.id}_{b.exchanger}')
        for m in self.markets: # 거래소 api
            m.get_config()
            logger.debug(f'{m.id}_{m.nickname}_ArbiBot')
        return

    def get_orderbook_info(self, markets):
        '''
        get orderbook info of exchangers
        :param markets:
        :return: list of orderbook_[{'okx':{'240330': {}}, {'byb': {'240401': {}, ...}
        '''
        logger.debug(f'get_orderbook_info_{self.botname}')
        if not markets:
            return True
        startTime = time.time()
        results = list()
        futures = dict()
        executor = ThreadPoolExecutor(max_workers=len(markets))
        for m in markets:
            futures[executor.submit(m.Orderbook)] = m
        for future in as_completed(futures):
            data = False
            try:
                data = future.result()
            except Exception as ex:
                results.append(data)
            else:
                results.append(data)
        logger.debug(f"get_orderbook_info time elapsed: {time.time() - startTime: .2f}")
        return results

    def seek_remainDates(self, given_date):
        # 현재 날짜 가져오기 (GMT 시간 기준)
        current_date = datetime.utcnow()
        # 주어진 날짜의 연도 가져오기 (20YY 형식으로 가정)
        given_year = int('20' + given_date[:2])
        given_month = int(given_date[2:4])
        given_day = int(given_date[4:6])

        # 주어진 날짜로 datetime 객체 생성
        given_datetime = datetime(given_year, given_month, given_day)
        # 현재 날짜와 주어진 날짜 간의 차이 계산
        difference = given_datetime - current_date
        # 남은 일수 가져오기
        # print(f"현재로부터 {difference.days}일이 남았습니다.")
        return difference.days


    def seek_premium_exch(self, exs, exb, binance):
        '''
        # seek_premium_2 exchangers
        results of orderBook  = {'okx': {'240330': {'5000': {}, ... }, }
        '''
        logger.debug('seek_premium_exch')
        exs_bid_price = dict()
        exs_bid_qty = dict()
        exs_ask_price = dict()
        exs_ask_qty = dict()
        exb_bid_price = dict()
        exb_bid_qty = dict()
        exb_ask_price =dict()
        exb_ask_qty = dict()
        optionInfo = list()

        if exs and exb and binance:
            # my_dict1과 my_dict2의 키 값 추출
            exname_s = list(exs.keys())[0]
            exname_b = list(exb.keys())[0]
            exs_ep = list(exs.values())[0] # inner dict of orderbook
            exb_ep = list(exb.values())[0]

            # 두 키 값에 해당하는 내부 딕셔너리의 키들을 구하고 교집합을 찾음
            common_expire_dates = list(set(exs_ep.keys()) & set(exb_ep.keys()))
            for expire_date in common_expire_dates:
                current_date = datetime.utcnow()
                if current_date.hour >= 8:
                    current_date += timedelta(days=1)
                # 현재 날짜를 '230805' 형식으로 변환
                current_date_string = current_date.strftime('%y%m%d')
                # 날짜 문자열을 datetime 객체로 변환
                current_date_obj = datetime.strptime(current_date_string, '%y%m%d')
                current_date_obj_plus_one_mon = current_date_obj + timedelta(days=31)
                compare_date_obj = datetime.strptime(expire_date, '%y%m%d')
                if current_date_obj_plus_one_mon < compare_date_obj:
                    logger.debug(f'too far expiration_{expire_date}_{self.botname}')
                    continue
                logger.debug(f'expiration date_{expire_date}')
                exs_option = exs_ep[expire_date]
                exb_option = exb_ep[expire_date]
                common_strikes =  set(exs_option.keys()) & set(exb_option.keys())
                for strike in common_strikes:
                    exs_strike = exs_option[strike]
                    exb_strike = exb_option[strike]
                    for optionType in ['C', 'P']:
                        exs_bid_price[optionType] = exs_strike[optionType]['bidPrice']
                        exs_ask_price[optionType] = exs_strike[optionType]['askPrice']
                        exb_bid_price[optionType] = exb_strike[optionType]['bidPrice']
                        exb_ask_price[optionType] = exb_strike[optionType]['askPrice']
                        exs_bid_qty[optionType]   = exs_strike[optionType]['bidQty']
                        exs_ask_qty[optionType]   = exs_strike[optionType]['askQty']
                        exb_bid_qty[optionType]   = exb_strike[optionType]['bidQty']
                        exb_ask_qty[optionType]   = exb_strike[optionType]['askQty']
                        margin = {
                            'coin': 'btc',
                            'exs': f'{exname_s}-{exname_b}',
                            'expire': expire_date,
                            'strike': strike,
                            'optionType': optionType,
                            'ask_price': exb_ask_price[optionType], # 매수거래소의 매도값
                            'bid_price': exs_bid_price[optionType], # 매도거래소의 매수값
                            'ask_qty': exb_ask_qty[optionType],
                            'bid_qty': exs_bid_qty[optionType],
                            'diff' : float(D(exb_ask_price[optionType]) - D(exs_bid_price[optionType])), # margin
                            'remainDate': self.seek_remainDates(expire_date),
                        }
                        optionInfo.append(margin)
                    '''
                    # bybit put 매수 okx call 매도
                    conversion = self.cal_conversion(bybit_p_ask_price * self.binance.asks_price, okx_c_bid_price , strike)
                    self.alert_signal(conversion, expire_date,'컨버젼', f'Bybit P 매수: {bybit_p_ask_price} \n Okx C 매도: {okx_c_bid_price} \n행사가격 : {strike} \n선물 : {self.binance.asks_price}')
                    # okx put 매수 bybit call 매도
                    conversion = self.cal_conversion(okx_p_ask_price , bybit_c_bid_price  * self.binance.asks_price, strike)
                    self.alert_signal(conversion,expire_date, '컨버젼', f'Okx P 매수: {okx_p_ask_price} \n Bybit C 매도: {bybit_c_bid_price} \n행사가격 {strike} \n선물 : {self.binance.asks_price}')
                    # bybit 풋 매도 , okx call 매수
                    reverisal = self.cal_reversial(bybit_p_bid_price * self.binance.bids_price, okx_c_ask_price , strike)
                    self.alert_signal(reverisal, expire_date,'리버셜', f'Bybit P 매도: {bybit_p_bid_price} \n Okx C 매수: {okx_c_ask_price} \n행사가격 {strike} \n선물 : {self.binance.bids_price}')
                    #okx 풋 매도 ,  bybit call 매수
                    reverisal = self.cal_reversial(okx_p_bid_price, bybit_c_ask_price * self.binance.bids_price, strike)
                    self.alert_signal(reverisal,expire_date, '리버셜',
                                      f'Okx P 매도: {okx_p_bid_price} \n Bybit C 매수: {bybit_c_ask_price} \n행사가격 {strike} \n선물 : {self.binance.bids_price}')
                    '''
            return optionInfo, common_expire_dates

    def get_premium_info(self, orderbooks):
        '''
        1. n 개 거래소에 대해 ask, bid 를 날짜별로 조사하여 margin 구한다.
        2. 2 개 거래소를 동시에 비교한다.
        3. 결과를 optionsInfo 로 전달한다.
        :param orderbookResults:
        :return:
        '''
        optionsInfo = list()
        expireDateInfo = list()
        binance = 70,000
        ex_ob_s_list = ex_ob_b_list = orderbooks
        for ex1 in ex_ob_s_list:
            for ex2 in ex_ob_b_list:
                if ex1 == ex2:
                    continue
                ex_s = ex1
                ex_b = ex2
                optionInfo, expireDate = self.seek_premium_exch(ex_s, ex_b, binance)
                optionsInfo.append(optionInfo)
                expireDateInfo.append(expireDate)
        return optionsInfo, expireDateInfo

    def arbi_main(self):
        logger.debug(f'Arbitrage Start_{self.botname}')
        self.arbitrage = Arbitrage.objects.get(id=self.id)  # Arbitrage
        time.sleep(self.arbitrage.period) if not self.arbitrage.dryrun else time.sleep(5)
        # if self.arbitrage.run == False:
        #     return
        logger.info(f'\n************** START[{self.loop_number}]_{self.botname}')
        orderbooks = self.get_orderbook_info(self.markets)
        for o in orderbooks:
            logger.debug(o)

        '''
        1. 동시 거래소 접근하여 orderbook 정보를 가져옴
        2. 정보는 optionsInfo 에 저장
        3. 2개 거래소씩 ask, bid 를 날짜별로 조사하여 정리
        '''
        if orderbooks:
            # {'okx': option4okx, 'byb': option4byb, ....}, 'eth': {}, }
            optionsInfo, expireDateInfo = self.get_premium_info(orderbooks)
            for op in optionsInfo:
                logger.debug(f'optionsInfo_{op}_{self.botname}')
                for k, v in op[0].items():
                    logger.debug(f'{k} : {v}')
                break
            # combined_optionsInfo = sorted(sum(optionsInfo, []), key=lambda x:(x['price'], -x['qty'])) #list(set(sum(optionsInfo, [])))
            combined_optionsInfo = sum(optionsInfo, [])
            combined_expireDateInfo = list(set(sum(expireDateInfo, [])))
            self.optionsInfo = combined_optionsInfo
            self.expireDateInfo = sorted(combined_expireDateInfo, key=lambda x:datetime.strptime(x, "%y%m%d"))
        return

    def run_arbi(self):
        # if not self.dryrun:
        #     time.sleep(random.randrange(1, 5))
        while True:
            self.arbi_main()
        return

    def loop(self):
        logger.debug(f'{self.botname} loop run')
        self.t1 = threading.Thread(target=self.run_arbi)
        if self.t1:
            self.t1.deamon = True
            self.t1.start()
        return

class Maker(object):
    def __init__(self):
        self.markets_b = ['bybit', 'binance', 'okx', 'deribit'];
        self.markets_s = ['okx', 'deribit']
        self.markets   = self.markets_b + self.markets_s
        self.symbols   = ['btc', 'eth']
        self.hds = dict() # { 'bybit-okx': hd of bybit-okx, ... }
        self.hd  = None # 특정 handler ex) bybit-okx, okx-okx
        self.hdid = None # 개별 hd id
        self.hds_setup()
        return

    def hds_setup(self, force=False):
        logger.debug('hds setup')
        if not self.hds or self.hdid == -1 or force:
            hds_conf = Arbitrage.objects.filter(enable=True)
            for hd_conf in hds_conf:
                if hd_conf.id not in self.hds.keys():
                    self.hds[hd_conf.id] = Handler(hd_conf) # specific Arbitrage
                    if force and not self.hds[hd_conf.id].t1:
                        self.hds[hd_conf.id].loop()
        return

    def main(self, request):
        return HttpResponse('ok')

    def getOptionsInfo(self, request):
        logger.debug('getOptionsInfo')
        context = dict()
        if request.method == 'POST':
            if request.POST.get('bot'):
                botid = int(request.POST.get('bot'))
                for k, hd in self.hds.items():
                    context['data'] = hd.optionsInfo if hd.optionsInfo else []
                    context['expireDate'] = hd.expireDateInfo if hd.expireDateInfo else []
                    context['result'] = 'success'
                    return HttpResponse(json.dumps(context))
        context['data']   = ''
        context['result'] = 'success'
        return HttpResponse(json.dumps(context))

    def index(self, request):
        print('index.html called')
        url = reverse('optionbd:index')
        print(url)
        return render(request, 'optionbd/index.html')

    def run(self):
        logger.debug('start run %d' % os.getpid())
        for i, bot in self.hds.items():
            bot.loop()
        return

maker = Maker()
maker.run()