script = """
<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<!-- Tether -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.7/js/tether.min.js"></script>
<!-- Bootstrap JS -->
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

<script>
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
        _objCheckOkxSession = setInterval(getOkxInstruments, 5000)
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

doOpenOkxRestApi();

</script>
"""