import streamlit as st
import requests
import pandas as pd
import numpy as np
from utils import get_logo

table_html = """
    <div class="wrap">
        <label for="expiration-date-select">만기일 선택:</label>
        <select id="expiration-date-select">
        <option value="all" selected>전체</option>
        </select>
        <button id="reload-button">새로 고침</button>

        <table id="tickers-table" class="display" style="width:100%;">
            <thead>
              <tr>
                <th>거래소</th>
                <th>코인 심볼</th>
                <th>만기일</th>
                <th>행사가</th>
                <th>옵션 유형</th>
                <th data-orderable="false">매도 호가</th>
                <th data-orderable="false">매도 수량</th>
                <th data-orderable="false">매수 호가</th>
                <th data-orderable="false">매수 수량</th>
                <th>차이</th>
                <th>남은 만기일</th>
              </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>
"""

from lightweight_charts.widgets import StreamlitChart
# Let's go!


if "symbols_list" not in st.session_state:
    st.session_state.symbols_list = None

st.set_page_config(
    layout='wide',
    page_title='Crypto Dashboard'
)

st.markdown(
    """
    <style>
        footer {display: none}
        [data-testid="stHeader"] {display: none}
    </style>
    """, unsafe_allow_html=True
)

with st.container():
    get_logo()

with st.sidebar:
    st.title("Option Premium")
    st.caption("Then you will know the truth, and the truth will set you free(John 8:32)")
    st.header("Settings")

    with st.form(key='params_form'):
        # st.markdown(f'<p class="params_text">CHART DATA PARAMETERS', unsafe_allow_html=True)
        #
        # st.divider()

        _symbols = ['BTC', 'ETH']
        symbols = st.multiselect('Coins', _symbols, key='symbols_selectbox')

        _buy_exchanges = ['Bybit', 'Binance', 'OKX', 'Deribit']
        buy_exchange = st.selectbox('Buy Exchange', _buy_exchanges, key='buy_exchange_selectbox')

        _sel_exchanges = ['OKX', 'Deribit']
        sel_exchange = st.selectbox('Sell Exchange', _sel_exchanges, key='sel_exchange_selectbox')

        st.markdown('')
        update_chart = st.form_submit_button('Update chart')
        st.markdown('')

empty1_col, howwork_col, empty1_col2, arbitrage_col, sign_col = st.columns([0.1, 5, 0.1, 5, 1])

with howwork_col:
    with st.expander("How it work", expanded=False):
        st.markdown("""
        1. Type in the 5️⃣ letters for your GUESS in each step (Start with **_ARISE_**! Trust me...). 
        2. Select the colors you get back from [WORDLE](https://www.nytimes.com/games/wordle/index.html) for each letter. 
        3. Press 'submit' to get the top suggestions for next guess.
    
        --- 
    
        ⚙️ Use the 👈 sidebar to change the settings.
    
        🎈 Share this app with your friends! 
    
        _Tip_: This app is meant to be used on a big screen 🖥 . If you are on a small screen 📱 turn it sideways for a better experience.
        """)

with arbitrage_col:
    with st.expander("Option Arbitrage", expanded=False):
        st.markdown("""
        1. Type in the 5️⃣ letters for your GUESS in each step (Start with **_ARISE_**! Trust me...). 
        2. Select the colors you get back from [WORDLE](https://www.nytimes.com/games/wordle/index.html) for each letter. 
        3. Press 'submit' to get the top suggestions for next guess.
    
        --- 
    
        ⚙️ Use the 👈 sidebar to change the settings.
    
        🎈 Share this app with your friends! 
    
        _Tip_: This app is meant to be used on a big screen 🖥 . If you are on a small screen 📱 turn it sideways for a better experience.
        """)

with sign_col:
    st.markdown('<p class="btc_text">Login</p>', unsafe_allow_html=True)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



api_key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjU1NmUyYjU0OThkNzVkYTM2NTQwNjczIiwiaWF0IjoxNzAwMjA2MTA3LCJleHAiOjMzMjA0NjcwMTA3fQ.XgQ28UjixbY3pWEAOPrYNVVkUW5P3NizNWgLRtiJCks'

title_col, emp_col, btc_col, eth_col, xmr_col, sol_col, xrp_col = st.columns([1, 0.2, 1, 1, 1, 1, 1])

with title_col:
    st.markdown('<p class="dashboard_title">Crypto<br>Dashboard</p>', unsafe_allow_html=True)

with btc_col:
    with st.container():
        btc_price = requests.get(
            f'https://api.taapi.io/price?secret={api_key}&exchange=binance&symbol=BTC/USDT&interval=1m')
        if 'value' in btc_price and btc_price['value']:
            btc_price = btc_price['value']
        else:
            btc_price = 0
        st.markdown(f'<p class="btc_text">BTC / USDT<br></p><p class="price_details">{btc_price}</p>',
        unsafe_allow_html=True)


with eth_col:
    with st.container():
        # eth_price = requests.get(
        #     f'https://api.taapi.io/price?secret={api_key}&exchange=binance&symbol=ETH/USDT&interval=1m').json()['value']
        eth_price = 2700000
        st.markdown(f'<p class="eth_text">ETH / USDT<br></p><p class="price_details">{eth_price}</p>',
                    unsafe_allow_html=True)

with xmr_col:
    with st.container():
        # xmr_price = requests.get(
        #     f'https://api.taapi.io/price?secret={api_key}&exchange=binance&symbol=XMR/USDT&interval=1m').json()['value']
        xmr_price = 700
        st.markdown(f'<p class="xmr_text">XMR / USDT<br></p><p class="price_details">{xmr_price}</p>',
                    unsafe_allow_html=True)

with sol_col:
    with st.container():
        sol_price = 2000000
        # sol_price = requests.get(
        #     f'https://api.taapi.io/price?secret={api_key}&exchange=binance&symbol=SOL/USDT&interval=1m').json()['value']
        st.markdown(f'<p class="sol_text">SOL / USDT<br></p><p class="price_details">{sol_price}</p>',
                    unsafe_allow_html=True)

with xrp_col:
    with st.container():
        xrp_price = 800
        # xrp_price = requests.get(
        #     f'https://api.taapi.io/price?secret={api_key}&exchange=binance&symbol=XRP/USDT&interval=1m').json()['value']
        st.markdown(f'<p class="xrp_text">XRP / USDT<br></p><p class="price_details">{xrp_price}</p>',
                    unsafe_allow_html=True)


empty1_col, params_col, empty2_col = st.columns([0.1, 10, 0.1])

with st.container():
        data = np.random.randn(5,7)
        columns = ['행사가격', '만기', '유형', '매수', '매도', '차익', '만기까지일자']
        df = pd.DataFrame(data=data, columns=columns)
        # st.dataframe(df)
        st.table(df)

import streamlit.components.v1 as components
from my_script import script as html_string

# Streamlit 앱의 제목 설정
# st.title("Streamlit with JavaScript Example")
#
# # 버튼을 클릭하면 JavaScript alert 메시지를 표시하는 Python 코드
if st.button("Click me"):
    components.html(html_string)
    st.markdown(html_string, unsafe_allow_html=True)
