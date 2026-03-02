import streamlit as st
from web.context import get_dividends_table

def frontend():
    st.title("Portfolio Quote")
    st.write("## Welcome to super-cow powered portfolio monitor!")
    st.write(str(get_dividends_table().all()))
    st.info("DONE")

frontend()
