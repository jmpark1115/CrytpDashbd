	//binace websocket info setting
	var _wSocket_binance_index
	var _binance_index_adress = "wss://fstream.binance.com/stream?streams="
	var _binance_index_markets= 'btcusdt@markPrice/ethusdt@markPrice/solusdt@markPrice/xrpusdt@markPrice';

	var EX_BINANCE = 'BINANCE';
	var EX_BINANC_MAP = {'BTCUSDT':'BTC','ETHUSDT':'ETH','SOLUSDT':'SOL','XRPUSDT':'XRP'};
	var SYMBOL_BTC = 'BTC';
	var SYMBOL_ETH = 'ETH';
	var SYMBOL_SOL = 'SOL';
	var SYMBOL_XRP = 'XRP';



	//binance websocket init
	function _binance_index_init() {

		wsAdress = _binance_index_adress + _binance_index_markets;
		_wSocket_binance_index = new WebSocket(wsAdress);

		_wSocket_binance_index.onopen = function(e) { _binance_open(e); };
		_wSocket_binance_index.onclose = function(e) { _binance_index_close(e); };
		_wSocket_binance_index.onmessage = function(e) { _binance_index_message(e) }
		_wSocket_binance_index.onerror = function(e) { _binance_index_error(e); };

	}

	//binance websocket open
	function _binance_index_open(e) {
		console.log("binance WebSocket opened!");
	}

	//binance websocket message process
	function _binance_index_message(e) {
		//JSON Object 변환 및 추출
		try{
			//console.log("===================================");
			//console.log("BINANCE MESSAGE : " + e.data);
			let binance_index = JSON.parse(e.data);
			//console.log("stream : " + binance_index['stream']);
			//console.log("Symbol : " + binance_index['data']['s']);
			//console.log("last price : " + binance_index['data']['i']);
			symbol = binance_index['data']['s'];
			index_price = binance_index['data']['i'];
			set_index_price_result(EX_BINANCE, EX_BINANC_MAP[symbol], index_price);

		}
		catch(e){
			console.log( "ERROR IN _binance_index_message : " + e.data );
		}
	}

    function set_index_price_result(exchange, symbol, index_price){
        //console.log(exchange + ' : ' +  symbol + ' : '+ price);

        if(exchange == EX_BINANCE && symbol == SYMBOL_BTC ){
            $("#binance_index_btc_price").text(formatNumberForBinanceIndex(index_price));
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_ETH){
            $("#binance_index_eth_price").text(formatNumberForBinanceIndex(index_price));
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_SOL){
            $("#binance_index_sol_price").text(formatNumberForBinanceIndex(index_price));
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_XRP){
            $("#binance_index_xrp_price").text(formatNumberForBinanceIndex(index_price));
        }else{
            console.log(exchange + ' : ' +  symbol + ' : '+ index_price);
        }

    }

    function formatNumberForBinanceIndex(numberString) {
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
	function _binance_index_error(e) {
		console.log( "BINANCE WebSocket ERROR : " + e.data );
	}

	//binance websocket close process
	function _binance_index_close() {
		console.log("BINANCE WebSocket closed!");
		_binance_index_init();
	}


	function doOpenBinanceIndex() {
		console.log('====> doOpenBinanceIndex');
		_binance_index_init();
	}

	function doCloseBinanceIndex() {
		console.log('====> doCloseBinanceIndex');
		if(typeof _wSocket_binance_index != "undefined"){
			_wSocket_binance_index.close();
			console.log("BINANCE  WebSocket closed!");
		}else{
			console.log("SKIP -> _wSocket_binance_index is " + _wSocket_binance_index);
		}
	}
