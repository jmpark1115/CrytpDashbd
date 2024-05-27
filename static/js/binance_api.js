
/*
//junegun lee
import threading
import hmac
import time
import json
import hashlib
import requests
import ssl

from decimal import Decimal as D
from decimal import getcontext
from websocket import WebSocketApp, enableTrace
from threading import Thread

try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode

import logging
logger = logging.getLogger(__name__)



SRC_URL = 'https://github.com/yasinkuyu/binance-trader/blob/master/app/BinanceAPI.py'
DOC_URL = 'https://binance-docs.github.io/apidocs/futures/en/#new-order-trade'
API_URL = 'https://fapi.binance.com' # 선물 API URL
WEB_URL = 'https://www.binance.com'
WSS_URL = 'wss://fstream.binance.com/ws'

class BinanceSocket(object):

    def __init__(self, symbol):
        self.symbol = symbol.lower()
        self.request_depth = json.dumps({"method": "unsubscribe", "params": [f"{symbol}@depth20"]})
        self.callback = self.message_handler
        self.data = dict()
        self.ws = None
        self.exited = False
        self.connect_key = ''
        self.secret_key = ''

    def _auth_url(self, url):
        # Generate expires.
        expires = int((time.time() + 1) * 1000)

        # Generate signature.
        signature = str(hmac.new(
            bytes(self.secret_key, "utf-8"),
            bytes(f"GET/realtime{expires}", "utf-8"), digestmod="sha256"
        ).hexdigest())

        param = "api_key={api_key}&expires={expires}&signature={signature}".format(
            api_key=self.connect_key,
            expires=expires,
            signature=signature
        )
        url = url + "?" + param
        return url

    def socket_init(self):
        logger.debug('init websocket and data store')
        # enableTrace(True)
        if self.ws:
            logger.debug('ws close')
            self.ws.close()
        self.ws = WebSocketApp(
            url=WSS_URL+f'/{self.symbol}@depth20',
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, msg: self.on_error(ws, msg),
            on_close=lambda ws: self.on_close(ws),
            on_open=lambda ws: self.on_open(ws))
        self.wst = Thread(target=lambda:self.ws.run_forever(ping_interval=60, ping_timeout=10, ping_payload="PING", sslopt={"cert_reqs": ssl.CERT_NONE}))
        self.wst.deamon = True
        self.wst.start()
        logger.debug(f'start socket_{self.symbol}')
        # Wait for connect before continuing
        conn_timeout = 5
        while not self.ws.sock or not self.ws.sock.connected:
            time.sleep(1)
            conn_timeout -= 1
            if conn_timeout < 0 :
                break
        if not self.ws.sock:
            logger.error(f'socket error_{self.symbol}')
        if conn_timeout < 0 :
            logger.error(f"Couldn't connect to WS! Exiting._{self.symbol}")
            self.exit()
        return

    def exit(self):
        logger.debug('exit')
        self.exited = True
        self.ws.close()

    def is_open(self):
        return not self.exited

    def on_message(self, ws, msg):
        if msg != b'pong_p':
            msg = json.loads(msg)
            self.callback(msg)

    def on_error(self, ws, msg):
        if not self.exited:
            logger.debug(f'on error : {msg}')

    def on_close(self, ws):
        logger.debug(f'on close')
        self.exited = True
        self.ws.close()

    def on_open(self, ws):
        logger.debug('on open')
        self.ws.send(self.request_depth)

    def message_handler(self, msg):
        if isinstance(msg, dict):
            if ('b' in msg and msg['b'] ) or ('a' in msg and msg['a']):
                self.data = msg
            else:
                self.data = dict()
        return
*/
console.log('binance function init executed successfully');
WSS_URL = 'wss://fstream.binance.com/ws'

var binanceTickers = {};
/*
DOC = "https://binance-docs.github.io/apidocs/voptions/en/#partial-book-depth-streams";
https://binance-docs.github.io/apidocs/voptions/en/#trade-streams
endpoint = 'wss://nbstream.binance.com/eoptions/ws/{symbol}@{channel}' #trade|ticker
channel : "index", "depth", "index", "kline", "markPrice", "openInterest", "ticker", "trade"
REFSRC = "https://github.com/SavosRU/binance-connector-REST-WebSocket/blob/52177255fbdf8563479f51089d20674323658758/core/websocket.js"
*/
    var _wSocket_binance_ticker;
    const _binance_URL = 'wss://fstream.binance.com';
    const symbol = 'btcusdt';
    const _binance_ticker_endpoint = '/ws/btcusdt@depth20@500ms';

    function _binance_ticker_init() {
//        wsAddress = _binance_URL + _binance_ticker_endpoint; //orderbook
        //wsAddress = "wss://nbstream.binance.com/eoptions"; ///stream";
        wsAddress = "wss://nbstream.binance.com/eoptions/ws/BTCUSDT@markPrice"; ///stream";
        _wSocket_binance_ticker = new WebSocket(wsAddress);

        _wSocket_binance_ticker.onopen = function(e) { _binance_ticker_open(e) };
        _wSocket_binance_ticker.onclose = function(e) { _binance_ticker_close(e) };
        _wSocket_binance_ticker.onmessage = function(e) { _binance_ticker_message(e) }
        _wSocket_binance_ticker.onerror = function(e) { _binance_ticker_error(e) };
    }

    function doOpenBinanceTicker() {
        console.log('====> doOpenBinanceOrderbook');
        _binance_ticker_init();
    }

    //binance ticker websocket open
    function _binance_ticker_open() {
        console.log("binance ticker WebSocket opened!");
        /*
        const url = "https://eapi.binance.com/eapi/v1/listenKey";
        $.ajax({
                async: true,
                url: url,
                type: 'POST',
                data: {},
                dataType: 'json',
                success: function(response) {
                    console.log('success_' + response.code);

                },
                error: function(response, status, err) {
                    console.log('error_' + status);
                },
        });
        */
    }

    function _binance_ticker_message(e) {
        //console.log( "binance ticker message : " + e.data );
        //JSON Object 변환 및 추출
        TickerData = JSON.parse(e.data);  //json 객체로 변환
        console.log("binance ticker length : " + TickerData.data.length); // attribte 호출 ok
        console.log("binance ticker MESSAGE : " + JSON.stringify(TickerData.data[0])); //문자열 + 문자열(json 문자열화)
        //console.log("binance tikcer msg : " + TickerData.data[0]); 문자열 + 객체 -> ng
        //console.log(TickerData.data.length);
        //console.log(TickerData.data[0]);
        binanceGetOptionTickers(TickerData.data);
    }

    //binance ticker websocket error process
    function _binance_ticker_error(e) {
        console.log( "binance ticker WebSocket ERROR : " + e.data );
    }

    //binance ticker websocket error process
    function _binance_ticker_close() {
        _wSocket_binance_ticker.close();
        console.log("binance ticker WebSocket closed!");
        console.log("binance ticker WebSocket will reopen!");
        doOpenBinanceTicker();
    }

    function binanceGetOptionTickers(data) {
        var tickers = {};
        const insts = data;
        for (let i=0; i<insts.length; i++) {
                let ticker = insts[i]['instId'].split('-');
                let coin = ticker[0];
                let expire_data = ticker[2];
                let strike = ticker[3];
                let side   = ticker[4];
                let refine_info = {};
                refine_info.askPrice = getRandomIntInRange(150, 200);
                refine_info.askQty = parseFloat(insts[i].askVol) || 0;
                refine_info.bidPrice = getRandomIntInRange(100, 150);;
                refine_info.bidQty = parseFloat(insts[i].bidVol) || 0;
                refine_info.timestamp = parseInt(insts[i].ts) || 0;
                refine_info.diff = refine_info.askPrice - refine_info.bidPrice;
                refine_info.remainDate = getRandomIntInRange(5, 15);

                if(!tickers.hasOwnProperty(coin)) {
                    tickers[coin] = {};
                }
                if(!tickers[coin].hasOwnProperty(expire_data)) {
                    tickers[coin][expire_data] = {};
                }
                if(!tickers[coin][expire_data].hasOwnProperty(strike)) {
                    tickers[coin][expire_data][strike] = {};
                }
                if(!tickers[coin][expire_data][strike].hasOwnProperty(side)) {
                    tickers[coin][expire_data][strike][side] = {};
                }
                tickers[coin][expire_data][strike][side] = refine_info
        }//for
        if (tickers) {
            //Tickers = {'binance': tickers};
            Tickers = tickers;
            console.log('binance ticker updated');
            return true;
        };
        console.log('! binance ticker not updated');
        return false;
    }

//_binance_ticker_init();
//console.log('binance ticker started');