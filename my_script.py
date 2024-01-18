script = """
<script>
		console.log("function init executed successfully");
		//GRID Size
		var _ORDERBOOK_SIZE = 7;
		var _TRADE_SIZE = 50;

		//binance websocket info setting
		var _wSocket_binance_orderbook;
		var _wSocket_binance_trade;
		var _wSocket_binance_price;
		var _binance_adress = 'wss://fstream.binance.com/ws/';
		var _binance_args_orderbook_XBTUSD = 'btcusdt@depth20@500ms';
		var _binance_args_trade_XBTUSD = 'btcusdt@aggTrade';
		var _binance_args_price_XBTUSD = 'btcusdt@markPrice@1s';
		var partialSellBinanceOrderBook = [];
		var partialBuyBinanceOrderBook = [];
		var partialBinanceTrade = [];
		var partialBinanceMarkPrice = 0;
		var partailBinanceIndexPrice = 0;

		//binance orderbook websocket init
		function _binance_orderbook_init() {

			wsAdress = _binance_adress + _binance_args_orderbook_XBTUSD;
			_wSocket_binance_orderbook = new WebSocket( wsAdress );

			_wSocket_binance_orderbook.onopen = function(e) { _binance_orderbook_open(e) };
			_wSocket_binance_orderbook.onclose = function(e) { _binance_orderbook_close(e) };
			_wSocket_binance_orderbook.onmessage = function(e) { _binance_orderbook_message(e) }
			_wSocket_binance_orderbook.onerror = function(e) { _binance_orderbook_error(e) };
		}

		//binance orderbook websocket open
		function _binance_orderbook_open() {
			console.log("BINANCE ORDERBOOK WebSocket opened!");
		}

		//binance Orderbook websocket error process
		function _binance_orderbook_close() {
			_wSocket_binance_orderbook.close();
			console.log("BINANCE ORDERBOOK WebSocket closed!");
			console.log("BINANCE ORDERBOOK WebSocket will reopen!");
			//doOpenBinanceOrderbook();
		}

		//binance orderbook websocket error process
		function _binance_orderbook_error(e) {
			console.log( "BINANCE ORDERBOOK WebSocket ERROR : " + e.data );
		}

		//binance orderbook websocket message process
		function _binance_orderbook_message(e) {
			//console.log("BINANCE ORDERBOOK MESSAGE :  : " + e.data);

			//JSON Object 변환 및 추출
			OrderData = JSON.parse(e.data);

			partialSellBinanceOrderBook = OrderData.a;
			//console.log( 'partialSellBinanceOrderBook.length : ' + partialSellBinanceOrderBook.length );
			partialBuyBinanceOrderBook = OrderData.b;
			//console.log( 'partialBuyBinanceOrderBook.length : ' + partialBuyBinanceOrderBook.length );

			if(isMakeBinanceOrderBook()){
				makeBinanceOrderBook();
			}
		}

		_previousBinanceMakeOrderBookTime = 0;
		_BinanceMakeOrderBookPeriod = 10000;
		function isMakeBinanceOrderBook() {
			timestamp = new Date().getTime();
			if(_previousBinanceMakeOrderBookTime + _BinanceMakeOrderBookPeriod > timestamp){
				console.log('========== skip');
				return false;
			}else{
				_previousBinanceMakeOrderBookTime =  new Date().getTime();
				console.log('========== makeOrdrBook');
				return true;
			}
		}

		function makeBinanceOrderBook() {

			console.log('=============== makeBinanceOrderBook start ===================');
			console.log( 'partialSellBinanceOrderBook.length : ' + partialSellBinanceOrderBook.length );
			console.log( 'partialBuyBinanceOrderBook.length : ' + partialBuyBinanceOrderBook.length );
			return true;

			//Setting cumulativeSum
			maxCumulativeSum = prepareBinanceOrderBookCumulativeSum(partialSellBinanceOrderBook , partialBuyBinanceOrderBook);
			//console.log('maxCumulativeSum : ' + maxCumulativeSum);

			//Sell : 앞에서 _ORDERBOOK_SIZE 만큼 자름, Buy : 앞에서 _ORDERBOOK_SIZE 만큼 자름
			partialSellBinanceOrderBookData = partialSellBinanceOrderBook.slice(0, _ORDERBOOK_SIZE);
			partialBuyBinanceOrderBookData = partialBuyBinanceOrderBook.slice(0, _ORDERBOOK_SIZE);

			$.each(partialSellBinanceOrderBookData, function(index, item){
				//Binace Sell의 경우 정렬순서 변경 필요
				tempIndex = (partialSellBinanceOrderBookData.length - index) - 1;
				trId = '#binance_sell_'+tempIndex;
				priceId = '#binance_sell_price_'+tempIndex;
				sizeId = '#binance_sell_size_'+tempIndex;
				amountId = '#binance_sell_amount_'+tempIndex;

				$(priceId).text(convertBinanceCurrency(new Number(item[0]).toFixed(2)));
				$(sizeId).text(new Number(item[1]).toFixed(3));
				$(amountId).text(convertBinanceCurrency(new Number(item[2]).toFixed(3)));
				//console.log('Binance Sell item[2] : ' + item[2]);

				//단일규모기준
				//$(trId).css('background-image',getBinanceOrderBookBackgroundImageStyle(item[1]));
				//총량기준
				//$(trId).css('background-image',getBinanceOrderBookBackgroundImageStyle(item[2]/maxCumulativeSum));

			});

			$.each(partialBuyBinanceOrderBookData, function(index, item){
				trId = '#binance_buy_'+index;
				priceId = '#binance_buy_price_'+index;
				sizeId = '#binance_buy_size_'+index;
				amountId = '#binance_buy_amount_'+index;
				$(priceId).text(convertBinanceCurrency(new Number(item[0]).toFixed(2)));
				$(sizeId).text(new Number(item[1]).toFixed(3));
				$(amountId).text(convertBinanceCurrency(new Number(item[2]).toFixed(3)));
				//console.log('Binance Buy item[2] : ' + item[2]);

				//단일규모기준
				//$(trId).css('background-image',getBinanceOrderBookBackgroundImageStyle(item[1]));
				//총량기준
				//$(trId).css('background-image',getBinanceOrderBookBackgroundImageStyle(item[2]/maxCumulativeSum));

			});

			//console.log('=============== makeBinanceOrderBook end ===================');

		}
    _binance_orderbook_init();

</script>
"""