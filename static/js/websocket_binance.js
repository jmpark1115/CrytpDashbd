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
		
		//binance trade websocket init 
		function _binance_trade_init() {
			
			wsAdress = _binance_adress + _binance_args_trade_XBTUSD;
			_wSocket_binance_trade = new WebSocket(wsAdress);	
			
			_wSocket_binance_trade.onopen = function(e) { _binance_trade_open(e) };
			_wSocket_binance_trade.onclose = function(e) { _binance_trade_close(e) };
			_wSocket_binance_trade.onmessage = function(e) { _binance_trade_message(e) }
			_wSocket_binance_trade.onerror = function(e) { _binance_trade_error(e) };
		}
		
		//binance price websocket init 
		function _binance_price_init() {
			
			wsAdress = _binance_adress + _binance_args_price_XBTUSD;
			_wSocket_binance_price = new WebSocket(wsAdress);	
			
			_wSocket_binance_price.onopen = function(e) { _binance_price_open(e) };
			_wSocket_binance_price.onclose = function(e) { _binance_price_close(e) };
			_wSocket_binance_price.onmessage = function(e) { _binance_price_message(e) }
			_wSocket_binance_price.onerror = function(e) { _binance_price_error(e) };
		}		
		
		//binance orderbook websocket open 
		function _binance_orderbook_open() {
			console.log("BINANCE ORDERBOOK WebSocket opened!");			
			
		}	
		
		//binance trade websocket open 
		function _binance_trade_open() {
			console.log("BINANCE Trade WebSocket opened!");	
		}		
		
		//binance price websocket open 
		function _binance_price_open() {
			console.log("BINANCE Price WebSocket opened!");	
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
		_BinanceMakeOrderBookPeriod = 0;
		function isMakeBinanceOrderBook() {
			
			timestamp = new Date().getTime();
			if(_previousBinanceMakeOrderBookTime + _BinanceMakeOrderBookPeriod > timestamp){
				//console.log('========== skip');
				return false;
			}else{
				_previousBinanceMakeOrderBookTime =  new Date().getTime();
				//console.log('========== makeOrdrBook');
				return true;
			}
			
		}			
		
		
		//binance trade websocket message process 	
		function _binance_trade_message(e) {
			//console.log("BINANCE TRADE MESSAGE :  : " + e.data);
			
			//JSON Object 변환 및 추출
			OrderData = JSON.parse(e.data);	
			
			_insert_binance_trade_data(OrderData);
			
			//_print_binance_trade_Data(partialBinanceTrade);
			
			//console.log("partialBinanceTrade.length :" + partialBinanceTrade.length );
			if(partialBinanceTrade.length > 0){
				makeBinanceTrade();
			}			
			
		}
		
		function _print_binance_trade_Data(partialBinanceTrade) {
			console.log( 'partialBinanceTrade.length : ' + partialBinanceTrade.length );
			
			$.each(partialBinanceTrade, function(index, item){ 
				console.log( "id :" + item.a 
						+ " , price :" + item.p
						+ " , size :" + item.q
						+ " , timestamp :" + item.T
						+ " , tickDirection :" + item.tickDirection );					
			});
			
		}

		var previousBinanceTradePrice  = 0;   
		var previousTicdretBinanceTickDirection  = 'plusTick'; 
		function _insert_binance_trade_data(item) {
			
			//최신정보를 앞에 삽입함
			partialBinanceTrade.unshift(item);
			
			//tickDirection 변수
			tickDirection = '';
			
			// 최초 Item이 추가된 경우
			if(partialBinanceTrade.length == 1){
				tickDirection = 'plusTick';
			}else{
				
				// Item이 계속 추가된 경우
				if(item.p == previousBinanceTradePrice){
					if('plusTick' == previousTicdretBinanceTickDirection || 'ZeroPlusTick' == previousTicdretBinanceTickDirection){
						tickDirection = 'ZeroPlusTick';
					}else{
						tickDirection = 'ZeroMinusTick';
					}
				}else if (item.p > previousBinanceTradePrice){
					if('plusTick' == previousTicdretBinanceTickDirection || 'ZeroPlusTick' == previousTicdretBinanceTickDirection){
						tickDirection = 'PlusTick';
					}else{
						tickDirection = 'plusTick';
					}						
				}else{
					if('plusTick' == previousTicdretBinanceTickDirection || 'ZeroPlusTick' == previousTicdretBinanceTickDirection){
						tickDirection = 'MinusTick';
					}else{
						tickDirection = 'MinusTick';
					}	
				}					
			}
							
			//item.tickDirection, previousBinanceTradePrice, previousBinanceTradePrice Setting
			item.tickDirection = tickDirection;
			previousTicdretBinanceTickDirection = item.tickDirection
			previousBinanceTradePrice = item.p;
			
			//partialBinanceTrade Resing 
			if(partialBinanceTrade.length > _TRADE_SIZE){
				partialBinanceTrade = partialBinanceTrade.slice(0, _TRADE_SIZE);
			}
						
			
		}
		
		//binance price websocket message process 	
		function _binance_price_message(e) {
			//console.log("BINANCE PRICE MESSAGE :  : " + e.data);
			
			//JSON Object 변환 및 추출
			OrderData = JSON.parse(e.data);	
			
			partialBinanceMarkPrice = OrderData.p;
			partailBinanceIndexPrice = OrderData.i;
			//console.log("partialBinanceMarkPrice :  : " + partailBinanceIndexPrice);
			//console.log("partailBinanceIndexPrice :  : " + partailBinanceIndexPrice);
			
			makeBinancePrice();
					
		}
		
		
		//binance orderbook websocket error process 	
		function _binance_orderbook_error(e) {
			console.log( "BINANCE ORDERBOOK WebSocket ERROR : " + e.data );
		}
		
		//binance trade websocket error process 	
		function _binance_trade_error(e) {
			console.log( "BINANCE Trade WebSocket ERROR : " + e.data );
		}
		
		//binance price websocket error process 	
		function _binance_price_error(e) {
			console.log( "BINANCE Price WebSocket ERROR : " + e.data );
		}

		//binance Orderbook websocket error process 	
		function _binance_orderbook_close() {
			_wSocket_binance_orderbook.close();
			console.log("BINANCE ORDERBOOK WebSocket closed!");
			console.log("BINANCE ORDERBOOK WebSocket will reopen!");
			doOpenBinanceOrderbook();
		}
		
		//binance Trade websocket error process 	
		function _binance_trade_close() {
			_wSocket_binance_trade.close();
			console.log("BINANCE Trade WebSocket closed!");
			console.log("BINANCE Trade WebSocket will reopen!");;
			doOpenBinanceTrade();
		}
		
		//binance Price websocket error process 	
		function _binance_price_close() {
			_wSocket_binance_price.close();
			console.log("BINANCE Price WebSocket closed!");
			console.log("BINANCE Price WebSocket will reopen!");;
			doOpenBinancePrice();
		}
		
		
	
		function doOpenBinanceOrderbook() {
			//console.log('====> doOpenBinanceOrderbook');
			_binance_orderbook_init();
		}
		function doCloseBinanceOrderbook() {
			//console.log('====> doCloseBinanceOrderbook');
			_binance_orderbook_close()
		}
		
		function doOpenBinanceTrade() {
			//console.log('====> doOpenBinanceTrade');
			_binance_trade_init();
		}
		
		function doCloseBinanceTrade() {
			//console.log('====> doCloseBinanceTrade');
			_binance_trade_close()
		}	
		
		
		function doOpenBinancePrice() {
			//console.log('====> doOpenBinancePrice');
			_binance_price_init();
		}
		
		function doCloseBinancePrice() {
			//console.log('====> doCloseBinancePrice');
			_binance_price_close()
		}					
		
		function makeBinanceOrderBook() {
			
			//console.log('=============== makeBinanceOrderBook start ===================');
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
		
		function prepareBinanceOrderBookCumulativeSum(partialSellBinanceOrderBook, partialBuyBinanceOrderBook) {
					
			tempSellSum = 0;
			tempBuySum = 0;
			maxSum = 0;
								
			$.each(partialSellBinanceOrderBook, function(index, item){ 
				tempSellSum = tempSellSum + (new Number(item[1]));
				item.push(tempSellSum);
			});
			
			
			$.each(partialBuyBinanceOrderBook, function(index, item){ 
				tempBuySum = tempBuySum + (new Number(item[1]));
				item.push(tempBuySum);
			});
				
			if(tempSellSum > tempBuySum){
				maxSum =  tempSellSum;
			}else{
				maxSum = tempBuySum;
			}
			//console.log('tempSellSum : ' + tempSellSum);
			//console.log('tempBuySum : ' + tempBuySum);
			//console.log('maxSum : ' + maxSum);
			return maxSum;
			
		}		
		
		function getBinanceOrderBookBackgroundImageStyle(size) {
			basePercent =  1;
			sizeToPercent = (size * 200) + basePercent;
			backgroundImageStyle='linear-gradient(to left, rgba(2, 199, 122, 0.25), rgba(2, 199, 122, 0.25) 0%, rgba(0, 0, 0, 0) ' + sizeToPercent +'%)';
			return backgroundImageStyle;
		}
		
 		function makeBinanceTrade() {
 			
			//console.log('=============== makeBinanceTrade start ===================');
			
			//Trade 챠트 생성을 위한 Data 구성
			partialBinanceTradeLength = partialBinanceTrade.length;
			$.each(partialBinanceTrade, function(index, item){ 
				
				tradeId = '#binance_trade_'+index;
				priceId = '#binance_trade_price_'+index;
				sizeId = '#binance_trade_size_'+index;
				timestampId = '#binance_trade_timestamp_'+index;
				recentPriceId = '#binance_trade_price_recent';	
					
				$(tradeId).css("display", "");	
				$(priceId).text(convertBinanceCurrency(new Number(item.p).toFixed(2)));
				$(sizeId).text(new Number(item.q).toFixed(3));
				$(timestampId).text(convertBinanceTime(item.T));				
				
				if('ZeroPlusTick' == item.tickDirection || 'plusTick' == item.tickDirection){
					$(priceId).removeClass('down');						
					$(sizeId).removeClass('down');	
					$(timestampId).removeClass('down');	
					$(priceId).addClass('up');
					$(sizeId).addClass('up');	
					$(timestampId).addClass('up');
					
					if(index == 0){
						$(recentPriceId).text(convertBinanceCurrency(new Number(item.p).toFixed(2)));
						$(recentPriceId).removeClass('down');
						$(recentPriceId).addClass('up');
					}	
					
				}else{
					$(priceId).removeClass('up');						
					$(sizeId).removeClass('up');	
					$(timestampId).removeClass('up');	
					$(priceId).addClass('down');
					$(sizeId).addClass('down');	
					$(timestampId).addClass('down');	
					
					if(index == 0){
						$(recentPriceId).text(convertBinanceCurrency(new Number(item.p).toFixed(2)));
						$(recentPriceId).removeClass('up');
						$(recentPriceId).addClass('down');
					}	
				}
			
			});
		
			//console.log('=============== makeBinanceTrade end ===================');
	
		}	
 		
 		function convertBinanceTime(duration) {
			KR_TIME_DIFF = 9 * 60 * 60 * 1000;

 			duration = duration + KR_TIME_DIFF;
			seconds = parseInt((duration/1000)%60);
			minutes = parseInt((duration/(1000*60))%60);
			hours = parseInt((duration/(1000*60*60))%24);
			
			hours = (hours < 10) ? "0" + hours : hours;
			minutes = (minutes < 10) ? "0" + minutes : minutes;
			seconds = (seconds < 10) ? "0" + seconds : seconds;
			
			return hours + ":" + minutes + ":" + seconds;
 	    }

 		function convertBinanceCurrency(strCurrency) {
	
			//console.log('strCurrency.indexOf : ' + strCurrency.indexOf('.'));
			
			strCurrency1 = '';
			strCurrency2 = '';
			
			if(strCurrency.indexOf('.') == -1){
				strCurrency1 = strCurrency.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
			}else{
				strCurrency1 = strCurrency.substring(0, strCurrency.indexOf('.'));
				strCurrency1 = strCurrency1.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
				strCurrency2 = strCurrency.substring(strCurrency.indexOf('.'), strCurrency.length);
			}
			
			//console.log('strCurrency : ' + strCurrency1 + strCurrency2 );
			return strCurrency1 + strCurrency2;
			
 	    }

		function makeBinancePrice() {
			markPriceId = '#binance_price_mark';
			indexPriceId = '#binance_price_index';
			$(markPriceId).text(convertBinanceCurrency(new Number(partialBinanceMarkPrice).toFixed(2)));
			$(indexPriceId).text(convertBinanceCurrency(new Number(partailBinanceIndexPrice).toFixed(2)));
		}
 		
		function doInitBinanceOrderBook() {
			
			for( index = 0 ; index < 50; index++){
				
				tradeId = '#binance_trade_'+index;
				
				sellPriceId = '#binance_sell_price_'+index;
				sellSizeId = '#binance_sell_size_'+index;
				sellAmountId = '#binance_sell_amount_'+index;
				
				buyPriceId = '#binance_buy_price_'+index;
				buySizeId = '#binance_buy_size_'+index;
				buyAmountId = '#binance_buy_amount_'+index;				
				
				recentPriceId = '#binance_trade_price_recent';
				
				markPriceId = '#binance_price_mark';
				indexPriceId = '#binance_price_index';
				
				if(index == 0){
					$(recentPriceId).text("");
					$(markPriceId).text("");
					$(indexPriceId).text("");
				}
				
				if(index < 7){
					$(sellPriceId).text('');
					$(sellSizeId).text('');
					$(sellAmountId).text('');
					$(buyPriceId).text('');
					$(buySizeId).text('');
					$(buyAmountId).text('');
				}
				
				$(tradeId).css("display", "none");
			}
			
		}		
		