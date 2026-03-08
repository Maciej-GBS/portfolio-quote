import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta
from portfolioq.db import Dividend
from portfolioq.web.context import get_dividends_table


@st.cache_data
def all_tickers():
    return ["abc", "def", "ghi"]

@st.cache_data
def all_years():
    return [2024, 2025, 2026]

@st.cache_data
def get_data(tickers):
    return [0.3, 0.2, 0.23, 0.17][:len(tickers)]


def figure_dividends_pie(tickers):
    fig = go.Figure([
        go.Pie(labels=tickers, values=get_data(tickers))
    ])
    return fig

def figure_dividends_bar(tickers):
    fig = go.Figure([
        go.Bar(x=tickers, y=get_data(tickers))
    ])
    return fig

def figure_dividends_time(tickers):
    fig = go.Figure([
        go.Scatter(x=[datetime.today(), datetime.today() - timedelta(days=30)], y=[1.0, 1.3], name="s1")
    ])
    return fig

def frontend():
    st.title("Dividend Payout")
    st.markdown("## Past dividends received")
    year = st.multiselect("Year", all_years())
    ticker = st.multiselect("Ticker", all_tickers())

    st.markdown("### Total payout rate")
    st.plotly_chart(figure_dividends_pie(ticker))

    st.markdown("### Payout rate per ticker")
    st.plotly_chart(figure_dividends_bar(ticker))

    st.markdown("### Payout over time")
    st.plotly_chart(figure_dividends_time(ticker))

frontend()
