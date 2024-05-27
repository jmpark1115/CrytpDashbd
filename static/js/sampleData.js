
var Tickers0 = {
    'okx': {
      'btc': {
        '240217': {
          '45000': {
            'C': {'price': 100, 'qty': 10, 'timestamp': 1234},
            'P': {'price': 101, 'qty': 11, 'timestamp': 4567}
          }
        }
      },
      'eth': {
        '240217': {
          '45000': {
            'C': {'price': 100, 'qty': 10, 'timestamp': 1234},
            'P': {'price': 101, 'qty': 11, 'timestamp': 4567}
          }
        }
      }
    },
    'binance': {
      'btc': {
        '240217': {
          '45000': {
            'C': {'price': 100, 'qty': 10, 'timestamp': 1234},
            'P': {'price': 101, 'qty': 11, 'timestamp': 4567}
          }
        }
      },
      'eth': {
        '240217': {
          '45000': {
            'C': {'price': 100, 'qty': 10, 'timestamp': 1234},
            'P': {'price': 101, 'qty': 11, 'timestamp': 4567}
          }
        }
      }
    },
    'debis': {
      'btc': {
        '240219': {
          '45000': {
            'C': {'price': 100, 'qty': 10, 'timestamp': 1234},
            'P': {'price': 101, 'qty': 11, 'timestamp': 4567}
          }
        }
      },
      'eth': {
        '240219': {
          '45000': {
            'C': {'price': 100, 'qty': 10, 'timestamp': 1234},
            'P': {'price': 101, 'qty': 11, 'timestamp': 4567}
          }
        }
      }
    }
};
// Tickers Original

var Tickers1 = {
        'btc': {
          '240217': {
            '45000': {
              'C': {'askPrice': 0, 'askQty': 10, 'bidPrice': 100, 'bidQty': 320, 'diff': 10, 'remainDate': '11'},
              'P': {'askPrice': 1, 'askQty': 10, 'bidPrice': 101, 'bidQty': 320, 'diff': 20, 'remainDate': '22'},
            }
          }
        },
        'eth': {
          '240218': {
            '46000': {
              'C': {'askPrice': 2, 'askQty': 10, 'bidPrice': 100, 'bidQty': 320, 'diff': 30, 'remainDate': '33'},
              'P': {'askPrice': 3, 'askQty': 10, 'bidPrice': 101, 'bidQty': 320, 'diff': 40, 'remainDate': '44'},
            }
          }
        }
       }
// Tickers1

var Tickers2 = {
        'btc': {
          '240217': {
            '45000': {
              'C': {'askPrice': 0, 'askQty': 10, 'bidPrice': 100, 'bidQty': 320, 'diff': 10, 'remainDate': '111'},
              'P': {'askPrice': 1, 'askQty': 10, 'bidPrice': 101, 'bidQty': 320, 'diff': 20, 'remainDate': '22'},
            }
          }
        },
                'eth': {
          '240218': {
            '46000': {
              'C': {'askPrice': 2, 'askQty': 10, 'bidPrice': 100, 'bidQty': 320, 'diff': 30, 'remainDate': '333'},
              'P': {'askPrice': 3, 'askQty': 10, 'bidPrice': 101, 'bidQty': 320, 'diff': 40, 'remainDate': '444'},
            }
          }
        }
       }
//Tickers2

var Tickers3 = [
        [
            {'ex': 'okx-byb', 'expire': 240217, 'strike': '13000', optionType: 'c', ask_price_s:'11', bid_price_b:'22', ask_qty_s:'33',bid_qty_b:'44', diff:'55', remainDate: '66'},
            {'ex': 'okx-byb', 'expire': 240217, 'strike': '13000', optionType: 'c', ask_price_s:'11', bid_price_b:'22', ask_qty_s:'33',bid_qty_b:'44', diff:'55', remainDate: '66'},
        ]
        [
            {'ex': 'okx-deribit', 'expire': 240217, 'strike': '13000', optionType: 'c', ask_price_s:'11', bid_price_b:'22', ask_qty_s:'33',bid_qty_b:'44', diff:'55', remainDate: '66'}
        ]
       ]
//Tickers2

var x = 1 ; // 초기값
async function getOptionTickersTest() {
    x++;
    let remainder = x % 2;
    if (remainder == 0) {
        console.log(`x: ${x}, remainder: ${remainder}`);
        return Tickers1;
    } else {
        return Tickers2;
    }
}