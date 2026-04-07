import streamlit as st
import portfolioq.mw as qmw
from portfolioq.web.context import get_dividends_table, get_trade_table, reset_db
from portfolioq.web.context import get_currency_converter

def load_nbp_data(files: list):
    converter = get_currency_converter()
    for f in files:
        converter.load_nbp_table(f)

@st.fragment
def nbp_data_frontend():
    st.markdown("### Currency rates")
    data = st.file_uploader("Official NBP csv tables", accept_multiple_files=True, type="csv")
    load_nbp_data(data)
    for f in data:
        st.info(f"Loaded successfully: {f.name}")

def load_ibkr_data(statements: list):
    trade_stream = qmw.IbkrTradeStream(statements)
    with get_trade_table() as tab:
        tab.insert(list(trade_stream))
    with get_dividends_table() as tab:
        for stmt in statements:
            dividend_stream = qmw.IbkrDividendStream(stmt)
            tab.insert(list(dividend_stream))

@st.fragment
def ibkr_data_frontend():
    st.markdown("### IBKR Client")
    data = st.file_uploader("Account activity statements in csv", accept_multiple_files=True, type="csv")
    load_ibkr_data(data)
    for f in data:
        st.info(f"Loaded successfully: {f.name}")

def generate_mock_data(num_dividends: int, num_trades: int):
    dividend_stream = qmw.MockDividendStream()
    trade_stream = qmw.MockTradeStream()
    with get_dividends_table() as tab:
        tab.insert([next(dividend_stream) for _ in range(num_dividends)])
    with get_trade_table() as tab:
        tab.insert([next(trade_stream) for _ in range(num_trades)])

@st.fragment
def mock_data_frontend():
    st.markdown("### Mock Client")
    n_dividends = st.number_input("# of dividends", min_value=0)
    n_trades = st.number_input("# of trades", min_value=0)

    if st.button("Generate mock data!"):
        generate_mock_data(n_dividends, n_trades)
        st.cache_data.clear()
        st.info("Data loaded!")

    if st.button("Reset DB"):
        reset_db()
        st.cache_data.clear()
        st.info("Database cleared!")

def frontend():
    st.title("Portfolio Quote")
    st.markdown("## Welcome to super-cow powered portfolio monitor!")
    nbp_data_frontend()
    st.divider()
    ibkr_data_frontend()
    st.divider()
    mock_data_frontend()

frontend()
