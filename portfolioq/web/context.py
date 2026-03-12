import streamlit as st
from portfolioq.db import DividendsTable, TradeTable, get_connector

def reset_db():
    with get_connector() as conn:
        for tab_name in [DividendsTable.NAME, TradeTable.NAME]:
            conn.get_cursor().execute(f"DROP TABLE IF EXISTS {tab_name};")
    get_dividends_table().create()
    get_trade_table().create()

@st.cache_resource
def get_dividends_table() -> DividendsTable:
    return DividendsTable()

@st.cache_resource
def get_trade_table() -> TradeTable:
    return TradeTable()
