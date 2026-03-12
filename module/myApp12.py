import streamlit as st

with st.expander('Expander 공간1'):
    st.write('냥이~~!')
    st.image('data/냥이.jpg', width=200)

with st.expander('Expander 공간2'):
    st.write('토끼~~!')
    st.image('data/토끼.jpg', width=200)
