import requests
import logging
from decimal import Decimal as D

logger = logging.getLogger(__name__)

try:
    from optionbd.models import *
except Exception as ex:
    logger.debug('import error %s %s' %(__file__, ex))
    # raise ValueError

API_DOCS = 'https://www.okx.com/docs-v5/en/#overview'
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
        self.get_config()
        return

    def http_request(self, method, path, params=None, headers=None, auth=None):
        url = API_URL + path
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=self.GET_TIME_OUT)
                if response.status_code == 200:
                    response = response.json()
                    return response
                elif response.status_code == 400: # {"code":-2013, "msg":"Order does not exist"}
                    response = response.json()
                    return response
                else:
                    logger.error('http_request_{}_{}_{}_{}'.format(method, url, params, response.text))
            if method == "POST":
                response = requests.post(url, params=params, headers=headers, timeout=self.POST_TIME_OUT)
                if response.status_code == 200:
                    response = response.json()
                    return response
                else:
                    logger.error('http_request_{}_{}_{}_{}'.format(method, url, params, response.text))
            if method == 'DELETE':
                response = requests.delete(url, params=params, headers=headers, timeout=self.POST_TIME_OUT)
                if response.status_code == 200:
                    response = response.json()
                    return response
                else:
                    logger.error('http_request_{}_{}_{}_{}'.format(method, url, params, response.text))
        except Exception as e:
            logger.error('http_request_{}_{}_{}'.format(url, params, e))

        return False

    def Instruments(self):
        '''
        GET /api/v5/public/instruments
        :return:
        '''
        path = '/api/v5/public/instruments'
        request = {
            'instType' : 'OPTION',
            'uly': self.symbol
        }
        res = self.http_request('GET', path, request)
        if res == False:
            return False
        if isinstance(res, dict):
            if 'price' in res:
                self.last = float(res['price']) *self.exrate
                return self.last
        return False

    def OptionMarketData(self):
        '''
        GET /api/v5/public/opt-summary
        :return:
        '''
        path = '/api/v5/public/opt-summary'
        request = {
            'instType' : 'OPTION',
            'uly': self.symbol
        }
        res = self.http_request('GET', path, request)
        print(res)

    # def OptionIndex(self, coin):
    def Ticker(self):
        '''
        Index 가격 가져오기
        coin : 'BTC', 'ETH', ....
        GET /api/v5/market/index-tickers
        :return: float
        '''
        try:
            path = '/api/v5/market/index-tickers'
            request = {
                'instType': 'OPTION',
                'instId': self.symbol
            }
            res = self.http_request('GET', path, request)
            if isinstance(res, dict):
                if 'data' in res and res['data']:
                    for i in res['data']:
                        price = float(i['idxPx'])
                        return price
        except Exception as ex:
            logger.error(f'Exception in IndexTickers {ex}')
        return 0

    # def OptionTickers(self, coin):
    def Orderbook(self):
        '''
        GET /api/v5/market/tickers
        :return:
        '''
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
                    indexPrice = self.Ticker()
                    if indexPrice <= 0:
                        return tickers
                    else:
                        indexPrice = str(indexPrice)
                    for data in res['data']:
                        ticker = data['instId'].split('-')
                        # coin = ticker[0]
                        expire_data = ticker[2]
                        strike = ticker[3]
                        side = ticker[4]
                        refine_info = dict()
                        refine_info['askPrice'] = float(D(data['askPx'])*D(indexPrice)) if data['askPx'] else 0
                        refine_info['askQty'] = float(D(data['askSz']) ) if data['askSz'] else 0
                        refine_info['bidPrice'] = float(D(data['bidPx'])* D(indexPrice)) if data['bidPx'] else 0
                        refine_info['bidQty'] = float(D(data['bidSz'])) if data['bidSz'] else 0
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
        except Exception as ex:
            logger.error(f'Exception in OptionTickers {ex}')
        return {self.exchanger: tickers}

    def OptionTicker(self, underlying, expire_date):
        '''
        GET /api/v5/market/tickers
        :return:
        '''
        path = '/api/v5/market/ticker'
        request = {
            'instId': 'BTC-USD-230606-26750-P'
        }
        res = self.http_request('GET', path, request)
        print(res)

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

if __name__ == "__main__":
    ex = Okx(0)
    d = ex.OptionTickers('ETH')
    print(d)