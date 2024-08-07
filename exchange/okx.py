import requests
import logging
from datetime import datetime, timedelta
from decimal import Decimal as D

logger = logging.getLogger(__name__)

try:
    from optionbd.models import *
except Exception as ex:
    logger.debug('import error %s %s' %(__file__, ex))
    # raise ValueError

API_URL = 'https://www.okx.com' # okx Api URL

class Okx(object):
    def __init__(self, id):
        self.id = id
        self.target = ''
        self.payment = ''
        self.symbol = ''  # ex) '%s%s' %(self.target, self.payment)
        self.exchanger = 'okx'
        self.nickname = ''  # 'okx'+'_'+str(id)+'_'+self.symbol
        self.type = ''
        self.GET_TIME_OUT = 30
        self.POST_TIME_OUT = 60
        self.tickers = dict()
        self.limit_day = 0 # 수집제한일 (0 = 제한없음)
        self.tr_fee_rate = 0.0003 # 거래수수료율 (0.03%)
        self.ex_fee_rate = 0.0002 # 행사수수료율 (0.02%)
        self.max_im_factor = {"BTC": 0.15, "ETH": 0.15} # BB 값으로 통일 (향후 교체 필요)
        self.get_config()
        return

    def get_config(self):
        try:
            bot_conf = ArbiBot.objects.get(id=self.id)
            self.target = bot_conf.target.upper()
            self.payment = bot_conf.payment.upper()
            self.type = bot_conf.type
            self.exchanger = bot_conf.exchanger.lower()
        except Exception as ex:
            self.target = 'BTC'
            self.payment = 'USD'
            self.type = ''
        self.symbol = f'{self.target}-{self.payment}' # BTC-USD
        self.nickname = self.exchanger+'_'+str(self.id)+'_'+self.symbol
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

    # def OptionIndex(self, coin):
    def get_index_price(self):
        '''
        Index 가격 가져오기
        coin : 'BTC', 'ETH', ....
        GET /api/v5/market/index-tickers
        :return: float
        '''
        index_name_mapping = {"BTC": "BTC-USD", "ETH": "ETH-USD"}
        try:
            path = '/api/v5/market/index-tickers'
            request = {
                'instType': 'OPTION',
                'instId': index_name_mapping[self.target]
            }
            res = self.http_request('GET', path, request)
            if isinstance(res, dict):
                if 'data' in res and res['data']:
                    for i in res['data']:
                        price = float(i['idxPx'])
                        return price
        except Exception as ex:
            logger.error(f'Exception in get_index_price {ex}')
        return 0

    # def OptionTickers(self, coin):
    def Orderbook(self):
        '''
        GET /api/v5/market/tickers
        :return:
        '''
        tickers_key = self.exchanger + "-" + self.target
        tickers = dict()
        path = '/api/v5/market/tickers'
        request = {
            'instType' : 'OPTION',
            'uly': self.symbol
        }
        try:
            res = self.http_request('GET', path, request)
            if isinstance(res, dict):
                if 'data' in res and res['data']:
                    # index 가격 가져오기
                    indexPrice = self.get_index_price()
                    if indexPrice <= 0:
                        # 이전 데이터 반환
                        return {self.exchanger: self.tickers, self.target: self.target}
                    else:
                        indexPrice = str(indexPrice)
                    # res 데이터 파싱
                    for data in res['data']:
                        ticker = data['instId'].split('-')
                        # coin = ticker[0]
                        expire_data = ticker[2]
                        if self.ticker_filter(expire_data):
                            continue

                        strike = ticker[3]
                        side = ticker[4]
                        refine_info = dict()
                        refine_info['askPrice'] = float(D(data['askPx'])*D(indexPrice)) if data['askPx'] else 0
                        refine_info['askQty'] = float(D(data['askSz']) ) if data['askSz'] else 0
                        refine_info['bidPrice'] = float(D(data['bidPx'])* D(indexPrice)) if data['bidPx'] else 0
                        refine_info['bidQty'] = float(D(data['bidSz'])) if data['bidSz'] else 0
                        refine_info['indexPrice'] = float(D(indexPrice))
                        refine_info['tr_fee_rate'] = self.tr_fee_rate
                        refine_info['ex_fee_rate'] = self.ex_fee_rate
                        refine_info['max_im_factor'] = self.max_im_factor
                        refine_info['timestamp'] = int(data['ts']) if data['ts'] else 0
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

    def ticker_filter(self, expire_data ):
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

    def OptionTickers(self, underlying):
        '''
        GET /api/v5/market/tickers
        :return:
        '''
        path = '/api/v5/market/tickers'
        request = {
            'instType' : 'OPTION',
            'uly': underlying
        }
        res = self.http_request('GET', path, request)
        print(res)

if __name__ == "__main__":
    ex = Okx(0)
    d = ex.OptionTickers('ETH-USD')
    print(d)