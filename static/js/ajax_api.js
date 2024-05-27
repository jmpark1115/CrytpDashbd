      console.log('ajax function init executed successfully');
      const GET_TIME_OUT = 30;
      const POST_TIME_OUT = 60;

      async function getOptionTickers() {
        console.log('getOptionTickers callled');
        var OptionTickers = {};
        debug:
        var params = {
            'mode': 'ok',
            'symbol': 'btc',
        };
        $.ajax({
            async: true,
            type: 'POST',
            data: {
                'csrfmiddlewaretoken' : '{{ csrf_token }}',
                'bot' : 0,
                'action' : 'apply',
                'params'  : $.param(params),
            },
            url : "{% url 'optionbd:getoptionsinfo' %}",
            dataType : "json",
            success : function(response) {
                if (response.result == 'success') {
                    return response.data;
                } else {
                    console.log('response error');
                }
            },
            error : function(error) {
                    alert('error : ' + error);
            }
        }); //ajax
      } // getOptionTickers()

      async function _getOptionTickers() {
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