	//binace websocket info setting
	var _wSocket_binance
	var _binance_adress = "wss://fstream.binance.com/stream?streams="
	var _binance_markets= 'btcusdt@ticker/ethusdt@ticker/solusdt@ticker';

	//upbit websocket info setting
	var _wSocket_upbit
	var _upbit_adress = "wss://api.upbit.com/websocket/v1"
	var _upbit_markets= '[{"ticket":"test"},{"type":"ticker","codes":["KRW-BTC","KRW-ETH","KRW-SOL","KRW-USDT"]}]';

	var EX_BINANCE = 'BINANCE';
	var EX_BINANC_MAP = {'BTCUSDT':'BTC','ETHUSDT':'ETH','SOLUSDT':'SOL'};
	var EX_UPBIT = 'UPBIT';
	var EX_UPBIT_MAP = {'KRW-BTC':'BTC','KRW-ETH':'ETH','KRW-SOL':'SOL','KRW-USDT':'USDT'};
	var SYMBOL_BTC = 'BTC';
	var SYMBOL_ETH = 'ETH';
	var SYMBOL_SOL = 'SOL';
	var SYMBOL_USDT = 'USDT';



	//binance websocket init
	function _binance_init() {

		wsAdress = _binance_adress + _binance_markets;
		_wSocket_binance = new WebSocket(wsAdress);

		_wSocket_binance.onopen = function(e) { _binance_open(e); };
		_wSocket_binance.onclose = function(e) { _binance_close(e); };
		_wSocket_binance.onmessage = function(e) { _binance_message(e) }
		_wSocket_binance.onerror = function(e) { _binance_error(e); };

	}

	//upbit websocket init
	function _upbit_init() {

		_wSocket_upbit = new WebSocket(_upbit_adress);
		_wSocket_upbit.binaryType = 'arraybuffer';

		_wSocket_upbit.onopen = function(e) { _upbit_open(e); };
		_wSocket_upbit.onclose = function(e) { _upbit_close(e) };
		_wSocket_upbit.onmessage = function(e) { _upbit_message(e) }
		_wSocket_upbit.onerror = function(e) { _upbit_error(e) };

	}

	//binance websocket open
	function _binance_open(e) {
		console.log("binance WebSocket opened!");
	}

	//upbit websocket open
	function _upbit_open(e) {
		console.log("upbit WebSocket opened!");
		_wSocket_upbit.send( _upbit_markets );

	}


	//binance websocket message process
	function _binance_message(e) {
		//JSON Object 변환 및 추출
		try{
			//console.log("===================================");
			//console.log("BINANCE MESSAGE : " + e.data);
			let binance_ticker = JSON.parse(e.data);
			//console.log("stream : " + binance_ticker['stream']);
			//console.log("Symbol : " + binance_ticker['data']['s']);
			//console.log("Open price : " + binance_ticker['data']['o']);
			symbol = binance_ticker['data']['s'];
			open_price = binance_ticker['data']['o'];
			set_price_result(EX_BINANCE, EX_BINANC_MAP[symbol], open_price);

		}
		catch(e){
			console.log( "ERROR IN _binance_message : " + e.data );
		}
	}

	//upbit websocket message process
	function _upbit_message(e) {
		//JSON Object 변환 및 추출, 바이너리 변환
		try{
			//console.log("===================================");
			let enc = new TextDecoder("utf-8");
			let arr = new Uint8Array(e.data);
			//console.log("UPBIT MESSAGE : " + enc.decode(arr));
			let upbit_ticker = JSON.parse(enc.decode(arr));
			let type = upbit_ticker['type'];
			if('ticker' == type) {
				code = upbit_ticker['code'];
				open_price = upbit_ticker['opening_price'];
				set_price_result(EX_UPBIT, EX_UPBIT_MAP[code], open_price);
			}

		}
		catch(e){
			console.log( "ERROR IN _upbit_message : " + e.data );
		}

	}

    function set_price_result(exchange, symbol, price){
        //console.log(exchange + ' : ' +  symbol + ' : '+ price);

        if(exchange == EX_BINANCE && symbol == SYMBOL_BTC ){
            $("#binance_btc_price").text(formatNumber(price));
        }else if(exchange == EX_UPBIT && symbol == SYMBOL_BTC){
            $("#upbit_btc_price").text(formatNumber(price));
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_ETH){
            $("#binance_eth_price").text(formatNumber(price));
        }else if(exchange == EX_UPBIT && symbol == SYMBOL_ETH){
            $("#upbit_eth_price").text(formatNumber(price));
        }else if(exchange == EX_BINANCE && symbol == SYMBOL_SOL){
            $("#binance_sol_price").text(formatNumber(price));
        }else if(exchange == EX_UPBIT && symbol == SYMBOL_SOL){
            $("#upbit_sol_price").text(formatNumber(price));
        }else if(exchange == EX_UPBIT && symbol == SYMBOL_USDT){
            $("#upbit_usdt_price").text(formatNumber(price));
        }else{
            console.log(exchange + ' : ' +  symbol + ' : '+ price);
        }

    }

    function formatNumber(numberString) {
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
	function _binance_error(e) {
		console.log( "BINANCE WebSocket ERROR : " + e.data );
	}

	//upbit websocket error process
	function _upbit_error(e) {
		console.log( "UPBIT WebSocket ERROR : " + e.data );
	}

	//binance websocket close process
	function _binance_close() {
		console.log("BINANCE WebSocket closed!");
		_binance_init();
	}

	//upbit  websocket close process
	function _upbit_close(e) {
		console.log("UPBIT WebSocket closed!");
		_upbit_init();

	}


	function doOpenBinance() {
		//console.log('====> doOpenBinance');
		_binance_init();
	}

	function doOpenUpbit() {
		console.log('====> doOpenUpbit');
		_upbit_init();
	}

	function doCloseBinance() {
		console.log('====> doCloseBinance');
		if(typeof _wSocket_binance != "undefined"){
			_wSocket_binance.close();
			console.log("BINANCE  WebSocket closed!");
		}else{
			console.log("SKIP -> _wSocket_binance is " + _wSocket_binance);
		}
	}

	function doCloseUpbit() {
		console.log('====> doClosUpbit');
		if(typeof _wSocket_upbit != "undefined"){
			_wSocket_upbit.close();
			console.log("UPBIT WebSocket closed!");
		}else{
			console.log("SKIP -> _wSocket_upbit is " + _wSocket_upbit);
		}
	}
