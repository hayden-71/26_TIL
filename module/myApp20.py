import streamlit as st
import pandas as pd
import time

st.title('Streamlit 캐시 실습✌️')

@st.cache_data
def cal_sum(a, b):
    time.sleep(5)
    return a + b

a = st.number_input('첫번째 숫자 입력', 0, 10, 1)
b = st.number_input('두번째 숫자 입력', 0, 10, 1)
''
# 계산 실행 버튼으로 함수 실행
if st.button('계산 실행 🧮', key=1):
    result = cal_sum(a, b)
    st.write(f'계산 결과 ▶ {result}')

# 캐시 삭제 버튼
if st.button('✔️ 전체 캐시 삭제', key=2):
    st.cache_data.clear()           # 현재 페이지에 있는 모든 캐시 삭제
    st.write('캐시 삭제 완! ')
''
'---'


@st.cache_data
def get_data(age):
    myDict = {'이름': '민정', '나이':age, '성별': '여'}
    df = pd.DataFrame(myDict, index=['회원정보'])
    time.sleep(3)
    return df

myAge = st.slider('나이 입력', 0, 100, 20)
''

if st.button('실행', key=3):
    result = get_data(myAge)
    st.write(result)

# 특정 함수만 캐시 삭제하기 (on_click에 함수명.clear)
if st.button('✔️ get_data 캐시 삭제', key=4, on_click=get_data.clear):
    get_data.clear()
    st.write('캐시 삭제 완!!')
