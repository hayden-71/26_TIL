import streamlit as st
import pandas as pd
import time

# 사용자 정의 함수 선언 및 캐시 적용
@st.cache_data
def get_data(name, age, gender):
    myDict = {'이름': name, '나이':age, '성별': gender}
    df = pd.DataFrame(myDict, index=['회원정보'])
    time.sleep(3)
    return df

# 폼 미적용 상태
name1 = st.text_input(label="**What's your name?**",
                     placeholder='이름을 입력하세요 ')
age1 = st.slider('How old are you?', 1, 100, 30)
gender1 = st.radio(label= 'What is your gender?',
                  options=['남', '여'])

st.write(get_data(name1, age1, gender1))

# strftime: 날짜 타입을 문자열로 변환
# %Y : 4자리 연도
# %m : 월
# %d : 일
st.write(f'현재 시각: {time.strftime('%H:%M:%S')}')
st.caption('⚠️값이 바뀔 때마다 전체 코드가 재실행됩니다.')

''
'---'

############ 폼 적용 ~~~~~~~~
# clear_on_submit=True : 제출 버튼을 누르면 기존 입력 내용들 초기화 (False는 그대로 있음 )
with st.form(key='Form1', clear_on_submit=True):
    name2 = st.text_input(label="**What's your name?**",
                     placeholder='이름을 입력하세요 ')
    age2 = st.slider('How old are you?', 1, 100, 30)
    gender2 = st.radio(label= 'What is your gender?',
                      options=['남', '여'])

    st.write(f'현재 시각: {time.strftime('%H:%M:%S')}')
    st.caption('⚠️값이 바뀌어도 최종 제출 전에는 코드 재실행 안 됩니당. 제출할 때마다 값은 초기화됩니다.')

    if st.form_submit_button('제출하기!'):
        st.write(get_data(name2, age2, gender2))
