import streamlit as st
import FinanceDataReader as fdr

# TODO: Make recursive wrapper function to maximize cache reusability

CACHE_INPUT = {
    
}

@st.cache
def get_price(ticker, start, end):
    # start = str(start)
    # end = str(end)

    df = fdr.DataReader(ticker, start, end)

    return df