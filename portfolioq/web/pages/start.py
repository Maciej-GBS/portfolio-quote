import streamlit as st
import portfolioq.mw as qmw
from portfolioq.web.context import get_dividends_table, get_trade_table, reset_db

def generate_mock_data(num_dividends: int, num_trades: int):
    dividend_stream = qmw.MockDividendStream()
    trade_stream = qmw.MockTradeStream()
    get_dividends_table().insert([next(dividend_stream) for _ in range(num_dividends)])
    get_trade_table().insert([next(trade_stream) for _ in range(num_trades)])

def frontend():
    st.title("Portfolio Quote")
    st.write("## Welcome to super-cow powered portfolio monitor!")

    n_dividends = st.number_input("# of dividends", min_value=0)
    n_trades = st.number_input("# of trades", min_value=0)

    if st.button("Generate mock data!"):
        generate_mock_data(n_dividends, n_trades)
        st.info("Data loaded!")

    if st.button("Reset DB"):
        reset_db()
        st.info("Database cleared!")

frontend()
