import pandas as pd
import streamlit as st
from portfolioq.db import Dividend, Trade
from portfolioq.web.context import get_dividends_table, get_trade_table
from portfolioq.web.context import all_years, get_filtered_data
from portfolioq.web.context import get_currency_converter, NbpConverter

def available_tax_years() -> list[int]:
    full_ls = all_years(get_dividends_table()) + all_years(get_trade_table())
    return sorted(set(full_ls))

def dividend_transform_layer_convert(obj: Dividend, converter: NbpConverter) -> dict:
    return {"amount": converter(obj.amount, obj.currency, obj.payoutDate),
            "withholdingTax": converter(obj.withholdingTax, obj.currency, obj.payoutDate)}

def dividend_transform_layer_round(obj: dict) -> dict:
    return {
        **obj,
        **{f"{k}_round": round(obj[k]) for k in obj}
    }

def dividend_tax(year: int) -> pd.DataFrame:
    data = get_filtered_data(get_dividends_table(), [year], tickers=[])
    converter = get_currency_converter()
    layers = [
        lambda obj: dividend_transform_layer_convert(obj, converter),
        dividend_transform_layer_round
    ]
    for layer in layers:
        data = map(layer, data)
    return pd.DataFrame(list(data))

def frontend():
    st.title("Tax")
    st.markdown("## Tax Estimate")
    tax_result = st.empty()
    st.divider()
    yr = st.selectbox("Year", options=available_tax_years())
    if st.button("Calculate") and yr:
        ctn = tax_result.container()
        taxes_on_dividends = dividend_tax(yr)
        ctn.dataframe(taxes_on_dividends.sum(axis=0))
        ctn.dataframe(taxes_on_dividends)

frontend()
