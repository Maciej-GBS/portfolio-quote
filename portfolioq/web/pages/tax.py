import pandas as pd
import streamlit as st
from portfolioq.db import Dividend, Trade
from portfolioq.web.context import get_dividends_table, get_trade_table
from portfolioq.web.context import all_years, get_filtered_data
from portfolioq.web.context import get_currency_converter

def available_tax_years() -> list[int]:
    full_ls = all_years(get_dividends_table()) + all_years(get_trade_table())
    return sorted(set(full_ls))

class DividendTransforms:
    def __init__(self, tax_rate: float):
        self.converter = get_currency_converter()
        self.tax_rate = tax_rate

    def __iter__(self):
        return iter(self.to_list())

    def layer_convert(self, obj: Dividend) -> dict:
        return {"ticker": obj.ticker,
                "amount": self.converter(obj.amount, obj.currency, obj.payoutDate),
                "withholdingTax": self.converter(obj.withholdingTax, obj.currency, obj.payoutDate)}

    def layer_tax(self, obj: dict) -> dict:
        return {**obj,
                "tax": self.tax_rate * obj["amount"]}

    def layer_round(self, obj: dict) -> dict:
        return {
            **obj,
            **{f"{k}_round": round(obj[k]) for k in obj if isinstance(obj[k], float)}
        }

    def to_list(self) -> list:
        return [
            self.layer_convert,
            self.layer_tax,
            self.layer_round
        ]

def dividend_tax(year: int, tax_rate: float) -> pd.DataFrame:
    data = get_filtered_data(get_dividends_table(), [year], tickers=[])
    transforms = DividendTransforms(tax_rate)
    for layer in transforms:
        data = map(layer, data)
    return pd.DataFrame(list(data)).set_index("ticker", append=True)

def frontend():
    st.title("Tax")
    st.markdown("## Tax Estimate")
    tax_result = st.empty()
    st.divider()
    yr = st.selectbox("Year", options=available_tax_years())
    tax_rate = st.number_input(
        "Tax Rate", min_value=0.0, max_value=1.0, value=0.19, step=0.01, format='%.2f')
    if st.button("Calculate") and yr:
        ctn = tax_result.container()

        taxes_on_dividends = dividend_tax(yr, tax_rate)
        ctn.markdown("### from dividends\n"
                     "- amount - total income\n"
                     "- withholdingTax - cost of the income (already paid tax)\n"
                     "- tax - estimated tax to pay (not excluding cost)")
        ctn.dataframe(taxes_on_dividends.sum(axis=0))
        ctn.dataframe(taxes_on_dividends)
        ctn.divider()

        # taxes_on_trades = trade_tax(yr, tax_rate)
        ctn.markdown("### from trades")
        ctn.divider()

        ctn.markdown("### Conversion stats")
        ctn.write(get_currency_converter().stats_)

frontend()
