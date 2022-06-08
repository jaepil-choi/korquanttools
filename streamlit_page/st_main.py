import streamlit as st

import pandas as pd
import matplotlib.pyplot as plt

## Custom libs
from korquanttools import pricevolume

plt.rc('font', family='Malgun Gothic')


st.title(':chart_with_upwards_trend: Finance Dashboard')
st.markdown('---')

APPS = [
    '1. Market Graph',
    '2. Market Map',
    '3. Market Grouping',
    '4. Event Analysis',    
    ]

with st.sidebar:
    dropbox = st.selectbox('Select app', APPS)

### Market Graph ###

## 주가/거래량 포함 다양한 정보 대시보드
# - AdjClose, AdjVolume, 
# - DollarVolume, 
# - CumReturn, Sharpe, MDD (From Quantstats)
# - HoldingPeriodReturn, 
# - Winners/Losers

if dropbox == APPS[0]:
    st.header(APPS[0])
    st.title('시장 정보를 확인합니다.')