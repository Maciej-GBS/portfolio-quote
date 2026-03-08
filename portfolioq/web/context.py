import streamlit as st
from portfolioq.db import DividendsTable, TradeTable

@st.cache_resource
def get_dividends_table() -> DividendsTable:
    return DividendsTable()

@st.cache_resource
def get_trade_table() -> TradeTable:
    return TradeTable()
