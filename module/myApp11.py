import streamlit as st

tab1, tab2 = st.tabs(['좌측', '우측'])

with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.header('컬럼_1', divider='red')
        st.image('data/냥이.jpg')
        st.caption('귀여운 냥이~~~!')

    with col2:
        st.header('컬럼_2', divider='orange')
        st.image('data/토끼.jpg')

    with col3:
        st.header('컬럼_3', divider='rainbow')
        st.image('data/쿼카.jpg')

with tab2:
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.header('컬럼_1', divider='red')
        st.image('data/냥이.jpg')
        st.caption('귀여운 냥이~~~!')

    with col2:
        st.header('컬럼_2', divider='orange')
        st.image('data/토끼.jpg')

    with col3:
        st.header('컬럼_3', divider='rainbow')
        st.image('data/쿼카.jpg')
