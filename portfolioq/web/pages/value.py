import streamlit as st
from portfolioq.web.context import get_currency_converter

def frontend():
    st.title("Value Change")
    st.markdown("## Portfolio value change")

    st.markdown("### Total relative profit")
    st.markdown("### Relative profit per ticker")
    st.markdown("### Absolute profit over time")
    st.markdown("### Performance over time")

frontend()
