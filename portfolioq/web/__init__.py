import streamlit as st

def main():
    nav_pages = [
            st.Page("pages/start.py", title="Start"),
            st.Page("pages/value.py", title="Value"),
            st.Page("pages/dividends.py", title="Dividends"),
            st.Page("pages/tax.py", title="Tax"),
        ]
    nav = st.navigation(nav_pages)

    st.set_page_config(page_title="Portfolio Quote",
                    layout="wide")

    nav.run()
