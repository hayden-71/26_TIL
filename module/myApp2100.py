import streamlit as st

with st.form('my'):
    a = st.number_input('1숫자', value=0)
    b = st.number_input('2숫자', value=0)

    bt = st.form_submit_button('계산하기')

if bt:
    st.write(a+b)
