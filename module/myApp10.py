import streamlit as st

tab1, tab2, tab3 = st.tabs(['Cat', 'Rabbit', 'Quaka'])

with tab1:
    st.header('탭_1', divider='red')
    st.image('data/냥이.jpg')
    st.caption('귀여운 냥이~~~!')

with tab2:
    st.header('탭_2', divider='orange')
    st.image('data/토끼.jpg')

with tab3:
    st.header('탭_3', divider='rainbow')
    st.image('data/쿼카.jpg')
