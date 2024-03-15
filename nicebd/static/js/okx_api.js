// 사용하지 마시요.
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

      async function getOptionTickers() {
        console.log('getOptionTickers callled');
        const path = '/api/v5/market/tickers';
        tickers = {};
        var idxPx = await getIndexTickers();
        console.log('!!! result of idxPx: ' + idxPx);
        if (typeof idxPx == 'undefined') {
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

    var xx = 1 ; // 초기값
    var Tickers1 = {
          'okx': {
            'btc': {
              '240217': {
                '45000': {
                  'C': {'askPrice': 110, 'askQty': 10, 'bidPrice': 100, 'bidQty': 320, 'diff': 10, 'remainDate': '45'},
                  'P': {'askPrice': 105, 'askQty': 10, 'bidPrice': 101, 'bidQty': 320, 'diff': 20, 'remainDate': '50'},
                }
              }
            },
           }
          }
    var Tickers2 = {
          'okx': {
            'btc': {
              '240217': {
                '45000': {
                  'C': {'askPrice': 110, 'askQty': 10, 'bidPrice': 100, 'bidQty': 320, 'diff': 10, 'remainDate': '45'},
                  'P': {'askPrice': 123, 'askQty': 10, 'bidPrice': 101, 'bidQty': 320, 'diff': 20, 'remainDate': '50'},
                }
              }
            },
           }
          }

    async function getOptionTickersTest() {
        x++;
        let remainder = x % 5;
        if (remainder == 0) {
            console.log(`x: ${x}, remainder: ${remainder}`);
            return Tickers1;
        } else {
            return Tickers2;
        }
    }

    async function main() {
      await getIndexTickers();
      const intervalId = setInterval(async () => {
        await getOptionTickers();
      }, 5000);
      console.log('Interval started with ID:', intervalId);
    }

//main();