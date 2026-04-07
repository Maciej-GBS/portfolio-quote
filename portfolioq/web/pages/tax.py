import pandas as pd
import streamlit as st
from portfolioq.db import Dividend, Trade
from portfolioq.web.context import get_dividends_table, get_trade_table
from portfolioq.web.context import all_years, get_filtered_data
from portfolioq.web.context import get_currency_converter

def available_tax_years() -> list[int]:
    full_ls = all_years(get_dividends_table()) + all_years(get_trade_table())
    return sorted(set(full_ls))

class TradeTransforms:
    def __init__(self, tax_rate: float):
        self.converter = get_currency_converter()
        self.tax_rate = tax_rate

    def __iter__(self):
        return iter(self.to_list())

    def layer_convert(self, obj: Trade) -> dict:
        try:
            buyValNorm = self.converter(obj.buyValue, obj.currency, obj.buyDate)
        except ValueError as e:
            print(e)
            buyValNorm = obj.buyValue
        sellValNorm = self.converter(obj.sellValue, obj.currency, obj.sellDate)
        return {"ticker": obj.ticker,
                "change": sellValNorm - buyValNorm,
                "cost": buyValNorm,
                "earnings": sellValNorm}

    def layer_tax(self, obj: dict) -> dict:
        return {**obj,
                "tax": max(0.0, self.tax_rate * obj["change"])}

    def layer_round(self, obj: dict) -> dict:
        return {
            **obj,
            **{f"{k}_round": (max(1, round(obj[k])) if obj[k] > 0.0 else 0)
               for k in obj if isinstance(obj[k], float)}
        }

    def to_list(self) -> list:
        return [
            self.layer_convert,
            self.layer_tax,
            self.layer_round
        ]

class DividendTransforms(TradeTransforms):
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

    def to_list(self) -> list:
        return [
            self.layer_convert,
            self.layer_tax,
            self.layer_round
        ]

def tax_data(table, transforms, year: int) -> pd.DataFrame:
    data = get_filtered_data(table, [year], tickers=[])
    for layer in transforms:
        data = map(layer, data)
    data = list(data)
    if len(data) > 0:
        return pd.DataFrame(data).set_index("ticker", append=True)
    return pd.DataFrame()

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

        taxes_on_dividends = tax_data(get_dividends_table(), DividendTransforms(tax_rate), yr)
        ctn.markdown("### from dividends\n"
                     "- amount - total income\n"
                     "- withholdingTax - cost of the income (already paid tax)\n"
                     "- tax - estimated tax to pay (based on amount only)")
        ctn.dataframe(taxes_on_dividends.sum(axis=0))
        ctn.dataframe(taxes_on_dividends)
        ctn.divider()

        taxes_on_trades = tax_data(get_trade_table(), TradeTransforms(tax_rate), yr)
        ctn.markdown("### from trades\n"
                     "- change - profits or loses")
        ctn.dataframe(taxes_on_trades.sum(axis=0))
        ctn.dataframe(taxes_on_trades)
        ctn.divider()

        ctn.markdown("### Conversion stats")
        ctn.write(get_currency_converter().stats_)

frontend()
