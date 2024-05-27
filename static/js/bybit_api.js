console.log('bybit function init executed successfully');

var bybitTickers = {};
/*
DOC = 'https://bybit-exchange.github.io/docs/v5/websocket/public/ticker'
SRC = 'https://github.com/bybit-exchange/pybit/blob/master/pybit/unified_trading.py#L106';
*/
    var _wSocket_bybit_ticker;
    const _bybit_URL = 'wss://stream.bybit.com/v5/public';
    const _bybit_ticker_endpoint = '/option';
    const _bybit_orderbook_endpoint = '/linear';

    function _bybit_ticker_init() {
        wsAddress = _bybit_URL + _bybit_ticker_endpoint;
        _wSocket_bybit_ticker = new WebSocket(wsAddress);

        _wSocket_bybit_ticker.onopen = function(e) { _bybit_ticker_open(e) };
        _wSocket_bybit_ticker.onclose = function(e) { _bybit_ticker_close(e) };
        _wSocket_bybit_ticker.onmessage = function(e) { _bybit_ticker_message(e) }
        _wSocket_bybit_ticker.onerror = function(e) { _bybit_ticker_error(e) };
    }

    function doOpenbybitTicker() {
        //console.log('====> doOpenBinanceOrderbook');
        _bybit_ticker_init();
    }

    //bybit ticker websocket open
    function _bybit_ticker_open() {
        console.log("bybit ticker WebSocket opened!");
        /*
        Additional information:
            https://bybit-exchange.github.io/docs/v5/websocket/public/ticker

        topic = "tickers.{symbol}"
        self.subscribe(topic, callback, symbol)

        req_id = str(uuid4())
        subscription_message = json.dumps(
            {"op": "subscribe", "req_id": req_id, "args": subscription_args}
        )
        */
        const subscribe_data_ticker = {
            "op": "subscribe",
            "args": ['ticker.BTC-21MAR24-70500-C']
        }
        const subscribe_data_orderbook = {
            "op": "subscribe",
            "args": ["orderbook.100.BTC"]
        }
        _wSocket_bybit_ticker.send(JSON.stringify(subscribe_data_orderbook));
    }

    function _bybit_ticker_message(e) {
        console.log( "bybit ticker message : " + e.data );
        //JSON Object 변환 및 추출
        TickerData = JSON.parse(e.data);  //json 객체로 변환
        return;
        console.log("bybit ticker length : " + TickerData.data.length); // attribte 호출 ok
        console.log("bybit ticker MESSAGE : " + JSON.stringify(TickerData.data[0])); //문자열 + 문자열(json 문자열화)
        //console.log("bybit tikcer msg : " + TickerData.data[0]); 문자열 + 객체 -> ng
        //console.log(TickerData.data.length);
        //console.log(TickerData.data[0]);
        bybitGetOptionTickers(TickerData.data);
    }

    //bybit ticker websocket error process
    function _bybit_ticker_error(e) {
        console.log( "bybit ticker WebSocket ERROR : " + e.data );
    }

    //bybit ticker websocket error process
    function _bybit_ticker_close() {
        _wSocket_bybit_ticker.close();
        console.log("bybit ticker WebSocket closed!");
        console.log("bybit ticker WebSocket will reopen!");
        doOpenbybitTicker();
    }

    function bybitGetOptionTickers(data) {
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
            //Tickers = {'bybit': tickers};
            Tickers = tickers;
            console.log('bybit ticker updated');
            return true;
        };
        console.log('! bybit ticker not updated');
        return false;
    }

//_bybit_ticker_init();
//console.log('bybit ticker started');