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
    from exchange.bn     import Bn
    from exchange.bb     import Bb
    from exchange.drb    import Drb
    from exchange.okx    import Okx
except Exception as ex:
    raise ValueError(ex)

from .models import *

import logging
logger = logging.getLogger(__name__)

from concurrent.futures import ThreadPoolExecutor, as_completed

db_migrate = False
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
        self.executeTime = ''
        self.limit_price_diff_percent = float(1.0)
        self.get_config()
        return

    def get_config(self):
        logger.debug(f'\nhandler get config_{self.botname}')
        self.arbitrage = Arbitrage.objects.get(id=self.id) #Arbitrage
        bots = self.arbitrage.arbibot.filter(enable=True) # ArbiBot
        # Exchanger API create
        self.markets = list()
        for b in bots:
            if b.exchanger == 'bb':
                self.markets.append(Bb(b.id))
            elif b.exchanger == 'bn':
                self.markets.append(Bn(b.id))
            elif b.exchanger == 'okx':
                self.markets.append(Okx(b.id))
            elif b.exchanger == 'drb':
                self.markets.append(Drb(b.id))
            else:
                logger.debug(f'Unsupported exchanger_{b.id}_{b.exchanger}')
        for m in self.markets: # 거래소 api
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
        difference_days = difference.days
        if difference.seconds > 0:
            difference_days = difference.days + 1
        # 남은 일수 가져오기
        # print(f"현재로부터 {difference_days}일이 남았습니다.")
        return difference_days


    def seek_premium_exch(self, exs, exb, coin):
        '''
        # seek_premium_2 exchangers
        results of orderBook  = {'okx': {'240330': {'5000': {}, ... }, }
        '''
        optionInfo = list()

        if exs and exb and coin:
            # my_dict1과 my_dict2의 키 값 추출
            exname_s = list(exs.keys())[0]
            exname_b = list(exb.keys())[0]
            exs_ep = list(exs.values())[0] # inner dict of orderbook
            exb_ep = list(exb.values())[0]
            logger.debug(f"seek_premium_exch - {exname_s}, {exname_b}, {coin}")

            # 두 키 값에 해당하는 내부 딕셔너리의 키들을 구하고 교집합을 찾음
            common_expire_dates = list(set(exs_ep.keys()) & set(exb_ep.keys()))
            for expire_date in common_expire_dates:

                exs_option = exs_ep[expire_date]
                exb_option = exb_ep[expire_date]
                common_strikes =  set(exs_option.keys()) & set(exb_option.keys())
                for strike in common_strikes:
                    exs_strike = exs_option[strike]
                    exb_strike = exb_option[strike]

                    # 비교할 exs_strike, exb_strike 의 key 값 검증
                    exs_strike_keys = list(exs_strike.keys())
                    exb_strike_keys = list(exb_strike.keys())

                    # 비교할 exs_strike, exb_strike 의 key 값 검증 후 Call, Put 옵션 값을 각각 비교
                    for optionType in ['C', 'P']:

                        # exs_strike_keys, exb_strike_keys 양쪽에 optionType 이 모두 존재하지 않으면 제외
                        if optionType not in exs_strike_keys or optionType not in exb_strike_keys:
                            continue

                        # bidPrice, askPrice 가 o인 경우 제외
                        if exs_strike[optionType]['bidPrice'] == 0:
                            continue
                        if exb_strike[optionType]['askPrice'] == 0:
                            continue

                        sell_price = float(D(exs_strike[optionType]['bidPrice'])) # SELL거래소 매수값
                        buy_price = float(D(exb_strike[optionType]['askPrice'])) # BUY거래소의 매도값
                        sell_qty = float(D(exs_strike[optionType]['bidQty'])) # SELL거래소 수량
                        buy_qty = float(D(exb_strike[optionType]['askQty'])) # BUY거래소의 수량
                        sell_tr_fee_rate = float(D(exs_strike[optionType]['tr_fee_rate']))  # SELL거래소 거래수수료
                        buy_tr_fee_rate = float(D(exb_strike[optionType]['tr_fee_rate']))  # BUY거래소의 거래수수료
                        sell_ex_fee_rate = float(D(exs_strike[optionType]['ex_fee_rate']))  # SELL거래소 거래수수료
                        buy_ex_fee_rate = float(D(exb_strike[optionType]['ex_fee_rate']))  # BUY거래소의 거래수수료
                        sell_max_im_factor = float(D(exs_strike[optionType]['max_im_factor'][coin]))  # SELL거래소 max im factor
                        buy_max_im_factor = float(D(exb_strike[optionType]['max_im_factor'][coin]))  # BUY거래소의 max im factor


                        # price_diff_percent 가 0 보다 작으면 Skip
                        price_diff = float(D(sell_price) - D(buy_price))
                        if price_diff < 0.0:
                            continue

                        # total_fee = index가격 * 0.095%
                        # 주의 : 일단 exs 기준으로 계산 (확인 필요)
                        sell_index_price = float(D(exs_strike[optionType]['indexPrice']))
                        buy_index_price = float(D(exb_strike[optionType]['indexPrice']))
                        sell_fee = (sell_index_price * sell_tr_fee_rate) + (sell_index_price * sell_ex_fee_rate) # SELL거래소 Fee
                        buy_fee = (buy_index_price * buy_tr_fee_rate) + (buy_index_price * buy_ex_fee_rate) # BUY거래소 Fee
                        total_fee = sell_fee + buy_fee

                        # 콜옵션 OTM (외가격) = max(행사가 - index가격, 0), 폿옵션 OTM (외가격) = max(index가격 - 행사가 , 0)
                        # otm index가격 : 양 거래소 index 가격의 평군

                        otm_index_price = (sell_index_price + buy_index_price) / 2
                        otm = 0.0
                        if optionType == 'C':
                            otm = max(float(D(strike)) - otm_index_price, 0.0)
                        else:
                            otm = max(otm_index_price - float(D(strike)), 0.0)

                        # total_margin = 매수 가격 + (인덱스 가격 * 매수 거래소 수수료율) + (Max IM Factor * 인덱스 가격) - OTM + 인덱스 가격 * 매도 거래소 수수료율)
                        # 명칭은 totol_cost로 변경
                        total_cost = buy_price + (buy_index_price + buy_tr_fee_rate) + (sell_max_im_factor * sell_index_price) - otm + (sell_index_price * sell_tr_fee_rate)

                        # EDGE($) (Q 1개당 예상이익) : sell_price - buy_price - total_fee
                        edge =  sell_price - buy_price - total_fee

                        # EFFECTIVENESS(%) : EDGE / TOTAL_MAR * 100
                        effectiveness = edge / total_cost * 100

                        margin = {
                            'coin': coin,
                            'exs': f'{exname_s}-{exname_b}',
                            'expire': expire_date,
                            'strike': strike,
                            'optionType': optionType,
                            'sell_price': self.format_float(sell_price, 1),  # 매도거래소의 매수값
                            'buy_price': self.format_float(buy_price, 1),  # 매수거래소의 매도값
                            'sell_qty': self.format_float(sell_qty),  # 매도거래소의 수량
                            'buy_qty': self.format_float(buy_qty),  # 매수거래소의 수량
                            'total_fee': self.format_float(total_fee, 1),  # 수수료 합계
                            'otm': self.format_float(otm, 1), # 매도거래소 외가격
                            'total_cost': self.format_float(total_cost, 1),  # 매매가능수량
                            'edge': self.format_float(edge, 1),  # 개당 이익
                            'qty': self.format_float(min(sell_qty, buy_qty)),
                            'effectiveness': self.format_float(effectiveness, 2),
                            'diff' : price_diff, # margin
                            'remainDate': self.seek_remainDates(expire_date),
                        }
                        optionInfo.append(margin)

            return optionInfo, common_expire_dates

    def format_float(self, float_number, decimal_places=None):
        rounded_number = float_number
        if decimal_places is not None and decimal_places >= 0:
            rounded_number = round(rounded_number, decimal_places)

        # .0으로 끝나는 경우 .0을 제거
        if str(rounded_number).endswith(".0"):
            rounded_number = int(rounded_number)

        # 3자리 마다 콤마 찍기
        rounded_number_str = f"{rounded_number:,}"

        return rounded_number_str

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
        ex_ob_s_list = ex_ob_b_list = orderbooks
        for ex1 in ex_ob_s_list:
            for ex2 in ex_ob_b_list:
                exname_1 = list(ex1.keys())[0]
                exname_2 = list(ex2.keys())[0]
                coin_1 = list(ex1.keys())[1]
                coin_2 = list(ex2.keys())[1]

                if exname_1 == exname_2:
                    continue
                if coin_1 != coin_2:
                    continue
                ex_s = ex1
                ex_b = ex2
                optionInfo, expireDate = self.seek_premium_exch(ex_s, ex_b, coin_1)
                optionsInfo.append(optionInfo)
                expireDateInfo.append(expireDate)
        return optionsInfo, expireDateInfo

    def arbi_main(self):
        logger.debug(f'Arbitrage Start_{self.botname}')

        # self.arbitrage = Arbitrage.objects.get(id=self.id)  # Arbitrage
        # time.sleep(self.arbitrage.period) if not self.arbitrage.dryrun else time.sleep(5)
        # if self.arbitrage.run == False:
        #     return

        logger.info(f'\n************** START[{self.loop_number}]_{self.botname}')
        orderbooks_raw = self.get_orderbook_info(self.markets)
        orderbooks = [o for o in orderbooks_raw if o and next(iter(o.values())) != {}]
        for o in orderbooks:
            logger.debug(next(iter(o)))

        '''
        1. 동시 거래소 접근하여 orderbook 정보를 가져옴
        2. 정보는 optionsInfo 에 저장
        3. 2개 거래소씩 ask, bid 를 날짜별로 조사하여 정리
        '''
        if orderbooks:
            # {'okx': option4okx, 'byb': option4byb, ....}, 'eth': {}, }
            optionsInfo, expireDateInfo = self.get_premium_info(orderbooks)

            '''
            for op in optionsInfo:
                logger.debug(f'optionsInfo_{self.botname}')
                for k, v in op[0].items():
                    logger.debug(f'{k} : {v}')
                break
            '''

            # combined_optionsInfo = sorted(sum(optionsInfo, []), key=lambda x:(x['price'], -x['qty'])) #list(set(sum(optionsInfo, [])))
            combined_optionsInfo = sum(optionsInfo, [])
            combined_expireDateInfo = list(set(sum(expireDateInfo, [])))
            self.optionsInfo = combined_optionsInfo
            self.expireDateInfo = sorted(combined_expireDateInfo, key=lambda x:datetime.strptime(x, "%y%m%d"))
            self.executeTime = self.set_execute_time()
        return

    def set_execute_time(self):
        """시스템 시간을 2024-06-03 13:18:41,166 형식으로 설정"""
        current_time = datetime.utcnow()
        current_time += timedelta(hours=9)  # 9시간 더하기
        return current_time.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]  # 마지막 3자리 잘라내기

    def run_arbi(self):
        # if not self.dryrun:
        #     time.sleep(random.randrange(1, 5))
        '''
        # 1회 실행 For 디버그
        self.arbi_main()
        '''
        while True:
            logger.debug(f'Arbitrage Period_{self.arbitrage.period}')
            if self.arbitrage.period > 0:
                logger.debug(f'Arbitrage Execution Is Sleeping For {self.arbitrage.period} Second')
                time.sleep(self.arbitrage.period)
                self.arbi_main()
            elif self.arbitrage.period == 0 :
                logger.debug(f'Arbitrage Execution Is Not Sleeping')
                time.sleep(self.arbitrage.period)
                self.arbi_main()
            else:
                logger.debug(f'Arbitrage Execution Is Stopped !!!')

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
        # self.markets_b = ['bybit', 'binance', 'okx', 'deribit'];
        # self.markets_s = ['okx', 'deribit']
        # self.markets   = self.markets_b + self.markets_s
        # self.symbols   = ['btc', 'eth']
        self.hds = dict() # { 'bybit-okx': hd of bybit-okx, ... }
        self.hd  = None # 특정 handler ex) bybit-okx, okx-okx
        self.hdid = None # 개별 hd id
        if not db_migrate:
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
        if request.method == 'GET':
            for k, hd in self.hds.items():
                context['data'] = hd.optionsInfo if hd.optionsInfo else []
                context['expireDate'] = hd.expireDateInfo if hd.expireDateInfo else []
                context['executeTime'] = hd.executeTime if hd.executeTime else []
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