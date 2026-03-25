import streamlit as st
from portfolioq.mw import NbpConverter
from portfolioq.db import Table, DividendsTable, TradeTable, get_connector
from portfolioq.db import Dividend, Trade

def reset_db():
    with get_connector() as conn:
        for tab_name in [DividendsTable.NAME, TradeTable.NAME]:
            conn.get_cursor().execute(f"DROP TABLE IF EXISTS {tab_name};")
    with get_dividends_table() as tab:
        tab.create()
    with get_trade_table() as tab:
        tab.create()

def get_dividends_table() -> DividendsTable:
    return DividendsTable()

def get_trade_table() -> TradeTable:
    return TradeTable()

@st.cache_resource
def get_currency_converter() -> NbpConverter:
    return NbpConverter()

def _hash_func(obj):
    return hash(obj)

@st.cache_data(hash_funcs={DividendsTable: _hash_func, TradeTable: _hash_func})
def all_years(tab: Table) -> list[int]:
    if isinstance(tab, DividendsTable):
        date_column = 'payoutDate'
    elif isinstance(tab, TradeTable):
        date_column = 'sellDate'
    else:
        raise TypeError(f"Table {type(tab)} does not support all_years selection")
    result = tab.query(f"SELECT DISTINCT CAST(strftime('%Y', {date_column}) AS INTEGER) as year "
                       f"FROM {tab.NAME} ORDER BY year ASC;")
    return [row[0] for row in result]

@st.cache_data(hash_funcs={DividendsTable: _hash_func, TradeTable: _hash_func})
def all_tickers(tab: Table) -> list[str]:
    if isinstance(tab, DividendsTable) or isinstance(tab, TradeTable):
        result = tab.query(f"SELECT DISTINCT ticker FROM {tab.NAME} ORDER BY ticker;")
        return [row[0] for row in result]
    raise TypeError(f"Table {type(tab)} does not support all_tickers selection")

@st.cache_data(hash_funcs={DividendsTable: _hash_func, TradeTable: _hash_func})
def get_filtered_data(tab: Table, years: list[int], tickers: list[str]) -> list:
    if isinstance(tab, DividendsTable):
        date_column = 'payoutDate'
        target_cls = Dividend
    elif isinstance(tab, TradeTable):
        date_column = 'sellDate'
        target_cls = Trade
    else:
        raise TypeError(f"Table {type(tab)} does not support filter_by_year_ticker selection")

    combined_filter = []
    if years:
        year_filter = f"CAST(strftime('%Y', {date_column}) AS INTEGER) IN ({','.join(str(y) for y in years)})"
        combined_filter.append(year_filter)
    if tickers:
        tickers = [f"'{t}'" for t in tickers]
        ticker_filter = f"ticker IN ({','.join(tickers)})"
        combined_filter.append(ticker_filter)

    if combined_filter:
        result = tab.query(f"SELECT * FROM {tab.NAME} WHERE {' AND '.join(combined_filter)};")
        return [target_cls(**{k:v for k,v in zip(target_cls.model_fields, kw)}) for kw in result]
    return tab.all()
