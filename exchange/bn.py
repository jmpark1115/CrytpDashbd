import asyncio
import threading
import concurrent.futures
from exchange.bnws import Bnws

import time
import requests
import logging
from datetime import datetime, timedelta
from decimal import Decimal as D

import logging
logger = logging.getLogger(__name__)

try:
    from optionbd.models import *
except Exception as ex:
    logger.debug('import error %s %s' %(__file__, ex))
    # raise ValueError

API_URL = 'https://eapi.binance.com/eapi/v1'

class Bn(object):
    def __init__(self, id):
        self.id = id
        self.target = ''
        self.payment = ''
        self.symbol = ''  # ex) '%s%s' %(self.target, self.payment)
        self.exchanger = 'bn'
        self.nickname = ''  # 'okx'+'_'+str(id)+'_'+self.symbol
        self.type = ''
        self.GET_TIME_OUT = 30
        self.POST_TIME_OUT = 60
        self.tickers = dict()
        self.req_interval = 20000
        self.limit_day = 0  # 수집제한일 (0 = 제한없음)
        self.previous_req_time = 0
        self.tr_fee_rate = 0.0003 # 거래수수료율 (0.03%)
        self.ex_fee_rate = 0.00015 # 행사수수료율 (0.015%)
        self.max_im_factor = {"BTC": 0.15, "ETH": 0.15} # BB 값으로 통일 (향후 교체 필요)
        self.t1 = None
        self.bnws = None
        self.get_config()
        return

    def get_config(self):
        try:
            bot_conf = ArbiBot.objects.get(id=self.id)
            self.target = bot_conf.target.upper()
            self.payment = bot_conf.payment.upper()
            self.type = bot_conf.type
            self.exchanger = bot_conf.exchanger.lower()
            # Bnws Start
            logger.debug('start loop_async')
            self.loop_async()
        except Exception as ex:
            self.target = 'BTC'
            self.payment = 'USD'
            self.type = ''
        self.symbol = f'{self.target}-{self.payment}' # BTC-USD
        self.nickname = self.exchanger+'_'+str(self.id)+'_'+self.symbol
        return

    def run_websocket(self):
        self.bnws = Bnws()
        # asyncio.run(self.bnws.connect_and_listen(self.target))
        loop = asyncio.new_event_loop()  # 새 이벤트 루프 생성
        asyncio.set_event_loop(loop)  # 현재 스레드의 이벤트 루프 설정
        loop.run_until_complete(self.bnws.connect_and_listen(self.target))
        loop.close()  # 이벤트 루프 종료

    def loop_async(self):
        self.t1 = threading.Thread(target=self.run_websocket)
        if self.t1:
            self.t1.deamon = True
            self.t1.start()
        return
    def http_request(self, method, path, params=None, headers=None, auth=None):
        url = API_URL + path
        response = False
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=self.GET_TIME_OUT)
            elif method == "POST":
                response = requests.post(url, params=params, headers=headers, timeout=self.POST_TIME_OUT)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=headers, timeout=self.POST_TIME_OUT)
            try:
                response = response.json()
            except Exception as ex:
                logger.debug(f'http_request_{method}_{url}_{params}_{response.text}')
            else:
                return response
        except Exception as ex:
            logger.error(f'http_request_{url}_{method}_{params}_{ex}')
        return False

    def get_index_price(self):
        '''
        Index 가격 가져오기
        index_name : 'ETHUSDT', 'BTCUSDT', ....
        GET /index
        :return: float
        '''
        index_name_mapping = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
        try:
            path = '/index'
            request = {
                'underlying': index_name_mapping[self.target]
            }
            res = self.http_request('GET', path, request)
            if isinstance(res, dict):
                if 'indexPrice' in res and res['indexPrice']:
                    price = float(res['indexPrice'])
                    return price
        except Exception as ex:
            logger.error(f'Exception in get_index_price {ex}')
        return 0


    def Orderbook(self):

        # 웹소켓 결과물 반환
        if self.bnws:
            return {self.exchanger: self.bnws.tickers, self.target: self.target}

        '''
        GET /ticker
        :return:
        '''
        tickers_key = self.exchanger + "-" + self.target
        tickers = dict()
        path = '/ticker'
        request = {
        }
        # 현재요청시간 - 과거요청시간의 차이가 self.req_interval 보다 클경우 요청 실행
        current_time_ms = int(round(time.time() * 1000))
        timd_diff = current_time_ms - self.previous_req_time
        logger.debug(f'timd_diff : {timd_diff}')
        if timd_diff > self.req_interval:
            logger.debug(f'previous_req_time is updated: {current_time_ms}')
            self.previous_req_time = current_time_ms
            try:
                res = self.http_request('GET', path, request)
                if isinstance(res, list):
                    # index 가격 가져오기
                    indexPrice = self.get_index_price()
                    if indexPrice <= 0:
                        # 이전 데이터 반환
                        return {self.exchanger: self.tickers, self.target: self.target}
                    else:
                        indexPrice = str(indexPrice)
                    # res 데이터 파싱
                    for data in res:
                        ticker = data['symbol'].split('-')
                        expire_data = ticker[1]
                        if self.ticker_filter(expire_data):
                            continue

                        strike = ticker[2]
                        side = ticker[3]
                        if self.target == ticker[0]:
                            refine_info = dict()
                            refine_info['askPrice'] = float(D(data['askPrice'])) if data['askPrice'] else 0
                            refine_info['askQty'] = 0
                            refine_info['bidPrice'] = float(D(data['bidPrice'])) if data['bidPrice'] else 0
                            refine_info['bidQty'] = 0
                            refine_info['indexPrice'] = float(D(indexPrice))
                            refine_info['tr_fee_rate'] = self.tr_fee_rate
                            refine_info['ex_fee_rate'] = self.ex_fee_rate
                            refine_info['max_im_factor'] = self.max_im_factor
                            refine_info['timestamp'] = int(data['openTime']) if data['openTime'] else 0
                            """
                            refine_info:
                            {'230607': {'23500': {'C': {'askPrice': '0.1285', 'askQty': '3510', 'bidPrice': '0.1205', 'bidQty': '3510', 'timestamp': '1686124069112'}}}}
                            """
                            # if not coin in tickers :
                            #     tickers[coin] = dict()
                            if not expire_data in tickers:
                                tickers[expire_data] = dict()
                            if not strike in tickers[expire_data]:
                                tickers[expire_data][strike] = dict()
                            if not side in tickers[expire_data][strike]:
                                tickers[expire_data][strike][side] = dict()
                            tickers[expire_data][strike][side] = refine_info
                    self.tickers = tickers
            except Exception as ex:
                logger.error(f'Exception in Orderbook {ex}')

        return {self.exchanger: self.tickers, self.target: self.target}

    def ticker_filter(self, expire_data):
        is_continue = False
        if self.limit_day > 0:
            try:
                # expire_data 에 따라 결과값 조정
                current_date = datetime.utcnow()
                if current_date.hour >= 8:
                    current_date += timedelta(days=1)

                # 현재 날짜를 '230805' 형식으로 변환
                current_date_string = current_date.strftime('%y%m%d')

                # 날짜 문자열을 datetime 객체로 변환
                current_date_obj = datetime.strptime(current_date_string, '%y%m%d')
                limit_date_obj = current_date_obj + timedelta(days=self.limit_day)
                expire_data_obj = datetime.strptime(expire_data, '%y%m%d')
                if limit_date_obj < expire_data_obj:
                    is_continue = True
            except Exception as ex:
                logger.error(f'Exception in ticker_filter {ex}')
        return is_continue

    def OptionTickers(self):
        '''
        GET /api/v5/market/tickers
        :return:
        '''
        path = '/ticker'
        request = {
        }
        res = self.http_request('GET', path, request)
        print(res)

if __name__ == "__main__":
    ex = Bn(0)
    d = ex.OptionTickers()
    # d = ex.Ticker()
    print(d)