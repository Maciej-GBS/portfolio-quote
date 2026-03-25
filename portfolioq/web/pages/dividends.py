import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from portfolioq.db import Dividend
from portfolioq.web.context import get_dividends_table, all_years, all_tickers, get_filtered_data
from portfolioq.web.context import get_currency_converter


def figure_dividends_pie(years, tickers):
    with get_dividends_table() as tab:
        data = get_filtered_data(tab, years, tickers)
    df = pd.DataFrame([
        (d.ticker, d.amount / d.marketValue) for d in data
    ], columns=['ticker', 'rate'])
    fig = go.Figure([
        go.Pie(labels=df['ticker'], values=df['rate'])
    ])
    return fig

def figure_dividends_bar(years, tickers):
    with get_dividends_table() as tab:
        data = get_filtered_data(tab, years, tickers)
    df = pd.DataFrame([
        (d.ticker, d.amount / d.marketValue) for d in data
    ], columns=['ticker', 'rate'])
    fig = go.Figure([
        go.Bar(x=df['ticker'], y=df['rate'])
    ])
    return fig

def figure_dividends_time(years, tickers):
    # data = get_filtered_data(get_dividends_table(), years, tickers)
    fig = go.Figure([
        go.Scatter(x=[], y=[], name="s1"),
    ])
    return fig

def frontend():
    st.title("Dividend Payout")
    st.markdown("## Past dividends received")
    with get_dividends_table() as tab:
        year = st.multiselect("Year", all_years(tab))
        ticker = st.multiselect("Ticker", all_tickers(tab))

    st.markdown("### Total payout rate")
    st.plotly_chart(figure_dividends_pie(year, ticker))

    st.markdown("### Payout rate per ticker")
    st.plotly_chart(figure_dividends_bar(year, ticker))

    st.markdown("### Payout over time")
    st.plotly_chart(figure_dividends_time(year, ticker))

frontend()
