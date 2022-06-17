import streamlit as st

import pandas as pd
import matplotlib.pyplot as plt

import quantstats as qs

## Custom libs
from korquanttools.pricevolume.loader import KRXPriceDM
from korquanttools.pricevolume.utils import DateUtil
import st_utils

plt.rc('font', family='Malgun Gothic')


st.title(':chart_with_upwards_trend: Finance Dashboard')
st.markdown('---')

APPS = [
    '0. About me',
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
    pass

if dropbox == APPS[1]:
    st.header(APPS[1])
    st.title('시장 정보를 확인합니다.')

    df = st_utils.get_price('KS11', "2017-01-01", "2022-04-30")

    returns = df['Change']
    st.line_chart(returns.cumsum())

    # st.pyplot(returns.plot())

    # st.pyplot(plt.plot(returns))

    st.pyplot(fig=qs.reports._plots.returns(returns, show=False))

### Market Map ### 

if dropbox == APPS[2]:
    START = 20220101
    END = 20220510

    pricevolume = KRXPriceDM(START, END)
    close_df = pricevolume.get_data('close')
    st.dataframe(close_df)
    

### Market Grouping ###

if dropbox == APPS[3]:
    pass

### Event Analysis ###

if dropbox == APPS[4]:
    pass