from websocket import WebSocketApp, enableTrace
import json
import requests
import logging
import datetime
logger = logging.getLogger(__name__)

API_URL = 'https://www.deribit.com/api/v2'
class Deribit:
    def __init__(self):
        self.GET_TIME_OUT = 30
        self.POST_TIME_OUT = 60

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
            'uly': 'BTC-USD'
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
            'uly': 'BTC-USD'
        }
        res = self.http_request('GET', path, request)
        print(res)

    def OptionTickers(self, coin):
        '''
        GET /api/v5/market/tickers
        :return:
        '''
        tickers = dict()
        path = '/public/get_book_summary_by_currency'
        request = {
            'kind' : 'option',
            'currency': coin
        }
        try:
            res = self.http_request('GET', path, request)
            if isinstance(res, dict) and res['result']:
                if res['result']:
                    for data in res['result']:
                        """
                        data:
                        {'symbol': 'BTC-28JUL23-22000-C', 'bid1Price': '0', 'bid1Size': '0', 'bid1Iv': '0', 'ask1Price': '0', 'ask1Size': '0', 'ask1Iv': '0', 'lastPrice': '0', 'highPrice24h': '0', 'lowPrice24h': '0', 'markPrice': '4903.96865002', 'indexPrice': '26580.02', 'markIv': '0.4534', 'underlyingPrice': '26655.35', 'openInterest': '0', 'turnover24h': '0', 'volume24h': '0', 'totalVolume': '0', 'totalTurnover': '0', 'delta': '0.89173413', 'gamma': '0.00004188', 'vega': '18.20399891', 'theta': '-8.37661804', 'predictedDeliveryPrice': '0', 'change24h': '0'}
                        """
                        ticker = data['instrument_name'].split('-')
                        coin = ticker[0]
                        date = datetime.datetime.strptime(ticker[1], '%d%b%y')
                        expire_data = date.strftime('%y%m%d')
                        strike = ticker[2]
                        side = ticker[3]

                        refine_info = dict()
                        refine_info['askPrice'] = float(data['ask_price'])  if data['ask_price'] else 0
                        refine_info['askQty'] =  0
                        refine_info['bidPrice'] = float(data['bid_price']) if data['bid_price'] else 0
                        refine_info['bidQty'] = 0
                        refine_info['timestamp'] = int(data['creation_timestamp']) if data['creation_timestamp'] else 0

                        if not coin in tickers:
                            tickers[coin] = dict()
                        if not expire_data in tickers[coin]:
                            tickers[coin][expire_data] = dict()
                        if not strike in tickers[coin][expire_data]:
                            tickers[coin][expire_data][strike] = dict()
                        if not side in tickers[coin][expire_data][strike]:
                            tickers[coin][expire_data][strike][side] = dict()
                        tickers[coin][expire_data][strike][side] = refine_info
                return tickers

        except Exception as ex:
            logger.error(f'Exception in Option Tickers {ex}')

        return tickers
    def OptionTicker(self, underlying, expire_date):
        '''
        GET /v5/market/tickers
        :return:
        '''
        path = '/v5/market/tickers'
        request = {
            'category': 'option',
            'baseCoin': 'BTC',
        }
        res = self.http_request('GET', path, request)
        print(res)

if __name__ == "__main__":
    # socket = OKXWebSocket()
    # socket.connect()
    ex = Deribit()
    d = ex.OptionTickers('BTC')
    print(d)