import asyncio
import websockets
import json, time

import requests
from datetime import datetime, timedelta
from decimal import Decimal as D

import logging
logger = logging.getLogger(__name__)

API_URL = 'https://eapi.binance.com/eapi/v1'
Wss_uri = "wss://nbstream.binance.com/eoptions/stream"

class Bnws:
    def __init__(self):
        self.api_url = API_URL
        self.wss_uri = Wss_uri
        self.loop_number = 0
        self.GET_TIME_OUT = 30
        self.POST_TIME_OUT = 60
        self.targets = ['BTC', 'ETH']
        self.target = ''
        self.index_price_map = {"BTC": 0.0, "ETH": 0.0}
        self.symbols = []
        self.tickers = dict()
        self.req_interval = 60000
        self.limit_day = 0  # 수집제한일 (0 = 제한없음)
        self.previous_req_time = 0
        self.tr_fee_rate = 0.0003 # 거래수수료율 (0.03%)
        self.ex_fee_rate = 0.00015 # 행사수수료율 (0.015%)
        self.max_im_factor = {"BTC": 0.15, "ETH": 0.15} # BB 값으로 통일 (향후 교체 필요)
        self.indexPrice = 0

    def http_request(self, method, path, params=None, headers=None, auth=None):
        url = self.api_url + path
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=self.GET_TIME_OUT)
                if response.status_code == 200:
                    response = response.json()
                    return response
                elif response.status_code == 400:  # {"code":-2013, "msg":"Order does not exist"}
                    response = response.json()
                    return response
                else:
                    logger.error(
                        'http_request_{}_{}_{}_{}'.format(method, url, params, response.text)
                    )
            if method == "POST":
                response = requests.post(
                    url, params=params, headers=headers, timeout=self.POST_TIME_OUT
                )
                if response.status_code == 200:
                    response = response.json()
                    return response
                else:
                    logger.error(
                        'http_request_{}_{}_{}_{}'.format(method, url, params, response.text)
                    )
            if method == 'DELETE':
                response = requests.delete(
                    url, params=params, headers=headers, timeout=self.POST_TIME_OUT
                )
                if response.status_code == 200:
                    response = response.json()
                    return response
                else:
                    logger.error(
                        'http_request_{}_{}_{}_{}'.format(method, url, params, response.text)
                    )
        except Exception as e:
            logger.error('http_request_{}_{}_{}'.format(url, params, e))

    def get_index_price(self, coin):
        '''
        Index 가격 가져오기
        index_name : 'ETHUSDT', 'BTCUSDT', ....
        GET /index
        :return: float
        '''
        index_name_mapping = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
        index_name = coin
        try:
            path = '/index'
            request = {
                'underlying': index_name_mapping[index_name]
            }

            res = self.http_request('GET', path, request)
            if isinstance(res, dict):
                if 'indexPrice' in res and res['indexPrice']:
                    price = float(res['indexPrice'])
                    self.index_price_map[index_name] = price
        except Exception as ex:
            logger.error(f'Exception in IndexTickers {ex}')


    def get_symbols(self, coin):
        '''
        GET /ticker
        :return:
        '''
        path = '/ticker'
        request = {}
        symbol_list = []

        try:
            res = self.http_request('GET', path, request)
            if isinstance(res, list):
                for data in res:
                    ticker = data['symbol'].split('-')
                    expire_data = ticker[1]
                    if ticker[0] == coin:
                        symbol_name = ticker[0] + "@ticker@" + expire_data
                        symbol_list.append(symbol_name)
                # symbol_list 중복제거
                self.symbols = list(set(symbol_list))
        except Exception as ex:
            logger.error(f'Exception in get_symbols {ex}')


    async def connect_and_listen(self, coin):

        self.target = coin
        logger.debug(f'Start Binance Websocket connect_and_listen for  : {self.target}')
        self.get_symbols(self.target)
        self.get_index_price(self.target)
        self.previous_req_time = int(round(time.time() * 1000))

        async with websockets.connect(self.wss_uri) as websocket:
            logger.debug(f'Start websocket.send for  : {self.target}')
            await websocket.send(json.dumps({"method": "SUBSCRIBE", "params": self.symbols, "id": 1}))

            # ping/pong 처리를 위한 task 생성
            ping_pong_task = asyncio.create_task(self.handle_ping_pong(websocket))

            try:
                async for message in websocket:

                    current_time_ms = int(round(time.time() * 1000))
                    timd_diff = current_time_ms - self.previous_req_time
                    # logger.debug(f'timd_diff : {timd_diff}')
                    if timd_diff > self.req_interval:
                        logger.debug(f'previous_req_time is updated: {current_time_ms}')
                        self.previous_req_time = current_time_ms
                        self.get_symbols(self.target)
                        self.get_index_price(self.target)
                        self.tickers = dict()
                        logger.debug(f'Restart websocket.send for  : {self.target}')
                        await websocket.send(json.dumps({"method": "SUBSCRIBE", "params": self.symbols, "id": 1}))

                    self.loop_number = self.loop_number + 1
                    res = json.loads(message)
                    # print(f"Received data for {self.loop_number} : {res}")
                    if isinstance(res, dict):
                        # res 데이터 파싱
                        if 'data' in res and res['data']:
                            for data in res['data']:
                                ticker = data['s'].split('-')
                                coin = ticker[0]
                                expire_data = ticker[1]
                                strike = ticker[2]
                                side = ticker[3]
                                # print(f"Received data for : {coin}-{expire_data}-{strike}-{side}")
                                if ticker[0] == self.target:
                                    refine_info = dict()
                                    refine_info['askPrice'] = float(D(data['ao'])) if data['ao'] else 0
                                    refine_info['askQty'] = float(D(data['aq'])) if data['aq'] else 0
                                    refine_info['bidPrice'] = float(D(data['bo'])) if data['bo'] else 0
                                    refine_info['bidQty'] = float(D(data['bq'])) if data['bq'] else 0
                                    refine_info['indexPrice'] = float(D(self.index_price_map[self.target]))
                                    refine_info['tr_fee_rate'] = self.tr_fee_rate
                                    refine_info['ex_fee_rate'] = self.ex_fee_rate
                                    refine_info['max_im_factor'] = self.max_im_factor
                                    refine_info['timestamp'] = int(data['T']) if data['T'] else 0

                                    if not expire_data in self.tickers:
                                        self.tickers[expire_data] = dict()
                                    if not strike in self.tickers[expire_data]:
                                        self.tickers[expire_data][strike] = dict()
                                    if not side in self.tickers[expire_data][strike]:
                                        self.tickers[expire_data][strike][side] = dict()
                                    self.tickers[expire_data][strike][side] = refine_info


                    keys = self.tickers.keys()
                    print(f"tickers.keys : {keys}")

            except websockets.exceptions.ConnectionClosed:
                logger.error(f'Connection closed : {self.target}')
            finally:
                # ping/pong task 취소
                ping_pong_task.cancel()


    async def handle_ping_pong(self, websocket):
        while True:
            try:
                # ping 프레임 수신 대기 (최대 10분)
                message = await asyncio.wait_for(websocket.recv(), timeout=600)
                if message == "ping":
                    # pong 프레임 응답
                    await websocket.send("pong")
                    logger.debug(f'Pong sent : {self.target}')
            except asyncio.TimeoutError:
                logger.debug(f'Connection timeout. Reconnecting...t : {self.target}')
                break
            except websockets.exceptions.ConnectionClosed:
                logger.debug(f'Connection closed. : {self.target}')
                break

if __name__ == "__main__":
    bnws = Bnws()
    coin = 'ETH'
    asyncio.run(bnws.connect_and_listen(coin))