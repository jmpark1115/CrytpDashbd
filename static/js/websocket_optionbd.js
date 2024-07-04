// const _websocket_adress = 'ws://localhost:8443';
// const _websocket_adress = 'ws://13.209.152.192:8443';
const _websocket_adress = 'wss://cryptopang.com/ws';
var _websocket;
var selectedExchange = [];
var selectedCoin = [];
var selectedOption = [];
var selectedExpiration = [];
var expirationDatesAll = [];
var optionData = {};

//option websocket init
function _option_init() {

    const currentTimeMillis = Date.now();
    const grade = 'vip';
    const paramStr = '?grade=' + grade + '&timestamp=' + currentTimeMillis;
    console.log(paramStr);

    _websocket = new WebSocket(_websocket_adress+paramStr);
    _websocket.onopen = function(e) { _option_open(e) };
    _websocket.onclose = function(e) { _option_close(e) };
    _websocket.onmessage = function(e) { _option_message(e) }
    _websocket.onerror = function(e) { _option_error(e) };

}

//option websocket open
function _option_open() {
    console.log("option webSocket opened !!!");
}

//option websocket close
function _option_close() {
    console.log("option webSocket closed !!!");
    console.log($('#isRestart').val());
    if($('#isRestart').val() == 'Y'){
        console.log("try reconnection !!!");
        _option_init();
    }
}

//option websocket open
function _option_error() {
    console.log( "option webSocket error : ", e.data );
}

//option websocket message process
function _option_message(e) {

    //console.log(event.data);
    //JSON Object 변환 및 추출
    jsonData = JSON.parse(event.data);
    optionData.expirationDates = jsonData.expireDate;
    optionData.tickers = jsonData.data;
    optionData.timestamp = jsonData.executeTime;
    updateTable(optionData);

}

// Option Datatable 갱신
function updateTable(optionData) {

    // OptionTickers가 유효하지 않으면 업데이트하지 않음
    if (!(optionData && optionData.tickers.length > 0 &&
       optionData.expirationDates && optionData.expirationDates.length>0)) {
        console.log("OptionTickers Invalid")
        return;
    }

    // 선택된 Exchange 수집
    selectedExchange = $('.exchange-checkbox:checked').map(function() {
        return this.value;
    }).get();

    // 선택된 Coin 수집
    selectedCoin = $('.coin-checkbox:checked').map(function() {
        return this.value;
    }).get();

    // 선택된 Option 수집
    selectedOption = $('.option-checkbox:checked').map(function() {
        return this.value;
    }).get();

    // 선택된 ExpireDate 수집
    selectedExpiration = $('.expiration-checkbox:checked').map(function() {
        return this.value;
    }).get();

    // ExpireDate 갱신
    populateExpirationCheckboxes(optionData.expirationDates, selectedExpiration);

    // range slider 값 비교를 위한 값 추출
    ptr_val = $('#profit-threshold').val();
    ptrs_text = $('#profit-threshold-span').text();
    due_val = $('#days-until-expiry').val();
    dues_text = $('#days-until-expiry-span').text();

    // 테이블 비우기
    table.clear();

    // 데이터 갱신 및 하이라이트 처리
    $.each(optionData.tickers, function(index, ticker) {

        // 선택한 exchange, coin, expire, option 순으로 일치여부 확인
        if (selectedExchange.includes('ALL') || selectedExchange.includes(ticker.exs)) {
            if (selectedCoin.includes('ALL') || selectedCoin.includes(ticker.coin)) {
                if (selectedExpiration.includes('ALL') || selectedExpiration.includes(ticker.expire)) {

                    if (due_val !== null && due_val.trim() !== '' && dues_text !== null && dues_text.trim() !== '') {
                        if ( getDaysDifference(ticker.expire) > parseInt(due_val) ) {
                            //console.log('ticker.expire : ' + ticker.expire);
                            //console.log('due_val : ' + due_val);
                            return true;
                        }
                    }

                    if (selectedOption.includes('ALL') || selectedOption.includes(ticker.optionType)) {

                        if (ptr_val !== null && ptr_val.trim() !== '' && ptrs_text !== null && ptrs_text.trim() !== '') {
                            if (ticker.edge < parseFloat(ptr_val)) {
                                return true;
                            }
                        }

                        const qty_detail = ticker.qty +":"+ticker.sell_qty+":"+ticker.buy_qty;
                        //console.log('qty_detail : ' + qty_detail)

                        table.row.add([
                            ticker.coin,
                            ticker.exs,
                            formatDate(ticker.expire),
                            ticker.strike,
                            ticker.optionType,
                            ticker.sell_price,
                            ticker.buy_price,
                            ticker.total_fee,
                            ticker.otm,
                            ticker.total_cost,
                            ticker.edge,
                            ticker.qty,
                            ticker.effectiveness,
                            ticker.remainDate,
                            qty_detail,
                        ]);

                    }
                }
            }
        }

    });

    // 테이블 다시 그리기
    table.draw();
}

//입력값(yymmdd)과 현재값을 차이 반환
function getDaysDifference(yymmdd) {
    dateString = '20' + yymmdd;
    const inputDate = new Date(dateString.substring(0, 4), parseInt(dateString.substring(4, 6)) - 1, dateString.substring(6, 8));
    const today = new Date();
    const diffInMillis = inputDate.getTime() - today.getTime();
    const diffInDays = Math.floor(diffInMillis / (1000 * 60 * 60 * 24));
    return diffInDays;
}

//dateString포멧(240927)을 27SEP24로 변경
function formatDate(dateString) {

  const date = parseInt(dateString);
  const year = Math.floor(date / 10000);
  const month = Math.floor((date % 10000) / 100);
  const day = date % 100;

  const monthNames = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
  const formattedMonth = monthNames[month - 1];

  return `${day}${formattedMonth}${year.toString().slice(-2)}`;
}

// ExpireDate Checkbox 갱신
function populateExpirationCheckboxes(expirationDates, selectedExpiration) {

    //console.log('expirationDates', expirationDates.toString());
    //console.log('selectedExpiration', selectedExpiration.toString());
    expirationDatesAll = expirationDatesAll.concat(expirationDates);
    expirationDatesAll = expirationDatesAll.filter((item, pos) => expirationDatesAll.indexOf(item) === pos).sort();
    //console.log('expirationDatesAll' ,expirationDatesAll.toString());

    // 기존 체크박스 제거 후 갱신
    const container = $('#expiration-date-checkboxes');
    container.empty();

    let allChecked = '';
    if(selectedExpiration.includes('ALL')){
        allChecked = 'checked'
    }
    // '전체' 선택 옵션 무조건 추가
    const allCheckboxHtml = `
        <div class="form-check form-check-inline" style="">
            <input class="form-check-input expiration-checkbox" type="checkbox" value="ALL" id="expire-all" ${allChecked}>
            <label class="form-check-label" for="expire-all">
                ALL
            </label>
        </div>
    `;
    container.prepend(allCheckboxHtml);

    expirationDatesAll.forEach(function(expireDate) {
        let checked = '';
        if(selectedExpiration.includes(expireDate)){
            checked = 'checked'
        }
        let displayMode = '';
        if(!expirationDates.includes(expireDate)){
            displayMode = 'display:none';
        }

        // 새로운 만료일만 추가
        const checkboxHtml = `
            <div class="form-check form-check-inline" style="${displayMode}">
                <input class="form-check-input expiration-checkbox" type="checkbox" value="${expireDate}" id="expire-${expireDate}" ${checked}>
                <label class="form-check-label" for="expire-${expireDate}">
                    ${formatDate(expireDate)}
                </label>
            </div>
        `;
        container.append(checkboxHtml);
    });


}


// Open option websocket
function doOpenOption() {
    //console.log('====> doOpenOptionTable');
    _option_init();
}

// close option websocket
function doCloseOption() {
  if (_websocket) {
    _websocket.close();
    _websocket = null;
  }
}