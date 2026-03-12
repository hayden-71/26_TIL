import streamlit as st

with st.sidebar:
    st.title('여기는 사이드바~~')
    st.header('중간 크기 타이틀')
    st.subheader('제일 작은 타이틀')
    '---'
    select = st.selectbox('다음 중 한가지 선택', ['부먹', '찍먹'])
    st.write(f'select 선택 = {select}')

# 컬럼 설정
# col1, col2, col3 = st.columns(3) # 만들고자 하는 컬럼 객체 수에 맞게 정수 입력
col1, col2, col3, _ = st.columns([1, 2, 1, 4]) # 리스트로 각 컬럼별 너비 비율 지정 가능

with col1:
    st.header('컬럼_1', divider='red')
    st.image('data/냥이.jpg', width=100)
    st.caption('귀여운 냥이~~~!')

with col2:
    st.header('컬럼_2', divider='orange')
    st.image('data/토끼.jpg')

with col3:
    st.header('컬럼_3', divider='rainbow')
    st.image('data/쿼카.jpg')
