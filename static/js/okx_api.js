      console.log('okk function init executed successfully');
      const GET_TIME_OUT = 30;
      const POST_TIME_OUT = 60;
      const API_URL = 'https://www.okx.com'

      var _objCheckOkxSession;

      function doOpenOkxRestApi() {
        if (_objCheckOkxSession == null) {
        } else {
            clearInterval(_objCheckOkxSession);
        }
        _objCheckOkxSession = setInterval(getOptionTickers(), 5000)
      }

      function getOkxInstruments() {
        //GET /api/v5/public/instruments
        console.log('getOkxInstruments called');
        const path = '/api/v5/public/instruments';
        $.ajax({
            async: true,
            url: API_URL + path,
            type: 'GET',
            data: {
                 'instType': 'OPTION',
                 'uly' : 'BTC-USD'
            },
            dataType: 'json',
            success: function(response) {
                console.log('success_' + response.code);
                let insts = response.data;
                for(let i=0; i<insts.length; i++) {
                    console.log('insts_' + insts[i]['instId'] + '_' + insts[i]['instType']);
                    break;
                }
            },
            error: function(response, status, err) {
                console.log('error_' + status);
            },
        }); //ajax
      } // getOkxInstruments

      async function getIndexTickers() {
        console.log('getIndexTickers called');
        const path = '/api/v5/market/index-tickers';
        const response = await $.ajax({
                //async: true,
                url: API_URL + path,
                type: 'GET',
                data: {
                     'instId' : 'BTC-USD'
                },
                dataType: 'json',
        });
        const insts = response.data;
        if (typeof insts === 'object') {
           let idxPx = parseFloat(insts[0].idxPx);
           console.log('idxPx = ' + idxPx);
           return idxPx;
        }
      } //getIndexTickers

      function getRandomIntInRange(min, max) {
        return Math.floor(Math.random() * (max-min) + min);
      }

      async function getOptionTickers() {
        console.log('getOptionTickers callled');
        const path = '/api/v5/market/tickers';
        var tickers = {};
        var idxPx = await getIndexTickers();
        console.log('!!! result of idxPx: ' + idxPx);
        if (typeof idxPx == 'undefined') {
            console.log('idxPx is undefined');
            return tickers;
        }
        const response = await $.ajax({
            //async: true,
            url: API_URL + path,
            type: 'GET',
            data: {
                 'instType' : 'OPTION',
                 'uly' : 'BTC-USD'
            },
            dataType: 'json',
        });

        console.log('success_' + response.code);
        const insts = response.data;
        if (typeof insts === 'object') {
            if (idxPx <= 0.0) {
                console.log('idxPx is invalid');
                return tickers;
            }
        }
        for(let i=0; i<insts.length; i++) {
            let ticker = insts[i]['instId'].split('-');
            let coin = ticker[0];
            let expire_data = ticker[2];
            let strike = ticker[3];
            let side   = ticker[4];
            let refine_info = {};
            refine_info.askPrice = parseFloat(insts[i].askPx)*idxPx || 0;
            refine_info.askQty = parseFloat(insts[i].askSz) || 0;
            refine_info.bidPrice = parseFloat(insts[i].bidPx)*idxPx || 0;
            refine_info.bidQty = parseFloat(insts[i].bidSz) || 0;
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
        } //for
        return tickers;
      } //getOptionTickers

    async function main() {
      await getIndexTickers();
      const intervalId = setInterval(async () => {
        await getOptionTickers();
      }, 5000);
      console.log('Interval started with ID:', intervalId);
    }

////////////////////////////////////////////////////////////////
var Tickers = {};
/*
https://www.okx.com/docs-v5/en/#overview-websocket
*/
    var _wSocket_okx_ticker;
    const _okx_URL = 'wss://ws.okx.com:8443';
    const _okx_ticker_endpoint = '/ws/v5/public';

    function _okx_ticker_init() {
        wsAddress = _okx_URL + _okx_ticker_endpoint;
        _wSocket_okx_ticker = new WebSocket(wsAddress);

        _wSocket_okx_ticker.onopen = function(e) { _okx_ticker_open(e) };
        _wSocket_okx_ticker.onclose = function(e) { _okx_ticker_close(e) };
        _wSocket_okx_ticker.onmessage = function(e) { _okx_ticker_message(e) }
        _wSocket_okx_ticker.onerror = function(e) { _okx_ticker_error(e) };
    }

    function doOpenOkxTicker() {
        //console.log('====> doOpenBinanceOrderbook');
        _okx_ticker_init();
    }

    //okx ticker websocket open
    function _okx_ticker_open() {
        console.log("okx ticker WebSocket opened!");
        const subscribe_data = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "opt-summary",
                    "instFamily": "BTC-USD"

                    //"channel": "tickers",
                    //"instFamily" : "BTC-USD" //-> ng
                    //"instFamily" : "BTCUSD" //-> ng

                    //"channel": "options",
                    //"instType": "OPTION",
                    //"instFamily" : "BTC-USD",
                    //"instId": "BTCUSD"
                }
            ]
        }
        _wSocket_okx_ticker.send(JSON.stringify(subscribe_data));
    }

    function _okx_ticker_message(e) {
        //console.log( "okx ticker message : " + e.data );
        //JSON Object 변환 및 추출
        TickerData = JSON.parse(e.data);  //json 객체로 변환
        console.log("okx ticker length : " + TickerData.data.length); // attribte 호출 ok
        console.log("okx ticker MESSAGE : " + JSON.stringify(TickerData.data[0])); //문자열 + 문자열(json 문자열화)
        //console.log("okx tikcer msg : " + TickerData.data[0]); 문자열 + 객체 -> ng
        //console.log(TickerData.data.length);
        //console.log(TickerData.data[0]);
        okxGetOptionTickers(TickerData.data);
    }

    //okx ticker websocket error process
    function _okx_ticker_error(e) {
        console.log( "okx ticker WebSocket ERROR : " + e.data );
    }

    //okx ticker websocket error process
    function _okx_ticker_close() {
        _wSocket_okx_ticker.close();
        console.log("okx ticker WebSocket closed!");
        console.log("okx ticker WebSocket will reopen!");
        doOpenOkxTicker();
    }

    function _okxGetOptionTickers(data) {
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
            //Tickers = {'okx': tickers};
            Tickers = tickers;
            console.log('okx ticker updated');
            return true;
        };
        console.log('! okx ticker not updated');
        return false;
    }

//_okx_ticker_init();
//console.log('okx ticker started');