import streamlit as st
import pandas as pd
from portfolioq.web.context import get_currency_converter, get_trade_table

def frontend():
    st.title("Value Change")
    st.markdown("## Portfolio value change")

    st.markdown("### Total relative profit")
    st.markdown("### Relative profit per ticker")
    st.markdown("### Absolute profit over time")
    st.markdown("### Performance over time")

    with get_trade_table() as tab:
        df = pd.DataFrame([x.model_dump() for x in tab.all()])
        st.dataframe(df)

frontend()
