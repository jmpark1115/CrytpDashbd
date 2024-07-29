	//binace websocket info setting
	var _wSocket_binance_ticker
	var _binance_ticker_adress = "wss://fstream.binance.com/stream?streams="
	var _binance_ticker_markets= 'btcusdt@ticker/ethusdt@ticker/bnbusdt@ticker/solusdt@ticker/etcusdt@ticker/xrpusdt@ticker/dogeusdt@ticker/bchusdt@ticker';

	var EX_BINANCE = 'BINANCE';
	var EX_BINANC_MAP = {'BTCUSDT':'BTC','ETHUSDT':'ETH','BNBUSDT':'BNB','SOLUSDT':'SOL','ETCUSDT':'ETC','XRPUSDT':'XRP','DOGEUSDT':'DOGE','BCHUSDT':'BCH'};
	var SYMBOL_BTC = 'BTC';
	var SYMBOL_ETH = 'ETH';
	var SYMBOL_BNB = 'BNB';
	var SYMBOL_SOL = 'SOL';
	var SYMBOL_ETC = 'ETC';
	var SYMBOL_XRP = 'XRP';
	var SYMBOL_DOGE = 'DOGE';
	var SYMBOL_BCH = 'BCH';


	//binance websocket init
	function _binance_ticker_init() {

		wsAdress = _binance_ticker_adress + _binance_ticker_markets;
		_wSocket_binance_ticker = new WebSocket(wsAdress);

		_wSocket_binance_ticker.onopen = function(e) { _binance_ticker_open(e); };
		_wSocket_binance_ticker.onclose = function(e) { _binance_ticker_close(e); };
		_wSocket_binance_ticker.onmessage = function(e) { _binance_ticker_message(e) }
		_wSocket_binance_ticker.onerror = function(e) { _binance_ticker_error(e); };

	}

	//binance websocket open
	function _binance_ticker_open(e) {
		console.log("binance WebSocket opened!");
	}

	//binance websocket message process
	function _binance_ticker_message(e) {
		//JSON Object 변환 및 추출
		try{
			//console.log("===================================");
			//console.log("BINANCE MESSAGE : " + e.data);
			let binance_ticker = JSON.parse(e.data);
			//console.log("stream : " + binance_ticker['stream']);
			//console.log("Symbol : " + binance_ticker['data']['s']);
			//console.log("last_price : " + binance_ticker['data']['c']);
			//console.log("change_percent : " + binance_ticker['data']['P']);
			symbol = binance_ticker['data']['s'];
			last_price = binance_ticker['data']['c'];
			change_percent = binance_ticker['data']['P'];
			set_ticker_price_result(EX_BINANCE, EX_BINANC_MAP[symbol], last_price, change_percent);

		}
		catch(e){
			console.log( "ERROR IN _binance_ticker_message : " + e.data );
		}
	}

    function set_ticker_price_result(exchange, symbol, price, change_percent){
        //console.log(exchange + ' : ' +  symbol + ' : '+ price + ' : '+ change_percent);
        let class_str = "";
        if (change_percent > 0){
            class_str = "change up";
        }else{
            class_str = "change down";
        }

        if(exchange == EX_BINANCE && symbol == SYMBOL_BTC ){
            $(".binance_ticker_btc_price").text(price);
            $(".binance_ticker_btc_change").text(change_percent);
            $(".binance_ticker_btc_change").removeClass("change up down");
            $(".binance_ticker_btc_change").addClass(class_str);
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_ETH){
            $(".binance_ticker_eth_price").text(price);
            $(".binance_ticker_eth_change").text(change_percent);
            $(".binance_ticker_eth_change").removeClass("change up down");
            $(".binance_ticker_eth_change").addClass(class_str);
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_BNB){
            $(".binance_ticker_bnb_price").text(price);
            $(".binance_ticker_bnb_change").text(change_percent);
            $(".binance_ticker_bnb_change").removeClass("change up down");
            $(".binance_ticker_bnb_change").addClass(class_str);
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_SOL){
            $(".binance_ticker_sol_price").text(price);
            $(".binance_ticker_sol_change").text(change_percent);
            $(".binance_ticker_sol_change").removeClass("change up down");
            $(".binance_ticker_sol_change").addClass(class_str);
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_ETC){
            $(".binance_ticker_etc_price").text(price);
            $(".binance_ticker_etc_change").text(change_percent);
            $(".binance_ticker_etc_change").removeClass("change up down");
            $(".binance_ticker_etc_change").addClass(class_str);
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_XRP){
            $(".binance_ticker_xrp_price").text(price);
            $(".binance_ticker_xrp_change").text(change_percent);
            $(".binance_ticker_xrp_change").removeClass("change up down");
            $(".binance_ticker_xrp_change").addClass(class_str);
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_DOGE){
            $(".binance_ticker_doge_price").text(price);
            $(".binance_ticker_doge_change").text(change_percent);
            $(".binance_ticker_doge_change").removeClass("change up down");
            $(".binance_ticker_doge_change").addClass(class_str);
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_BCH){
            $(".binance_ticker_bch_price").text(price);
            $(".binance_ticker_bch_change").text(change_percent);
            $(".binance_ticker_bch_change").removeClass("change up down");
            $(".binance_ticker_bch_change").addClass(class_str);
        }else{
            console.log(exchange + ' : ' +  symbol + ' : '+ price + ' : '+ change_percent);
        }

    }

    function formatNumberForBinanceTicker(numberString) {
        if (typeof numberString !== 'string') {
            numberString = String(numberString);
        }
        const parts = numberString.split('.');
        const integerPart = parts[0];
        const decimalPart = parts.length > 1 ? '.' + parts[1].substring(0, 2) : '';
        const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        return formattedInteger + decimalPart;
    }

	//binance websocket error process
	function _binance_ticker_error(e) {
		console.log( "BINANCE WebSocket ERROR : " + e.data );
	}

	//binance websocket close process
	function _binance_ticker_close() {
		console.log("BINANCE WebSocket closed!");
		_binance_ticker_init();
	}


	function doOpenBinanceTicker() {
		console.log('====> doOpenBinanceTicker');
		_binance_ticker_init();
	}

	function doCloseBinanceTicker() {
		console.log('====> doCloseBinanceTicker');
		if(typeof _wSocket_binance_ticker != "undefined"){
			_wSocket_binance_ticker.close();
			console.log("BINANCE  WebSocket closed!");
		}else{
			console.log("SKIP -> _wSocket_binance_ticker is " + _wSocket_binance_ticker);
		}
	}
