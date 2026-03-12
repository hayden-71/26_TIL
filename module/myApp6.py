
import streamlit as st
import datetime

# 선택 슬라이더
sel_slider = st.select_slider('추천 정도', ['매우 추천', '추천', '보통', '비추', '매우 비추'])
st.write(f'추천도 = {sel_slider}')

''
'---'
''

# 슬라이더 (정수 입력)
# value: 초기값, step: 최소단위(디폴트1)
slider = st.slider('점수는?', min_value=0, max_value=10, value=5, step=1)
st.write(f'점수 = {slider}')

''
'---'
''

# 숫자 입력 (+, -로 수치값 변경)
num_input = st.number_input('이번 시험 점수는? ',
                           min_value=0, max_value=100, value=0, step=5)
st.write(f'시험점수 = {num_input}')

''
'---'
''

# 텍스트 입력 
txt_input = st.text_input('당신의 이름은?')

# 날짜 입력 (날짜 구간은 디폴트로 현재기준 10년 전부터 10년후까지, max_value로 최대치 설정 가능)
d_input = st.date_input('당신의 생일은?', max_value=datetime.datetime.now())

# 시간 입력 (seconds, minutes, hours로 구간 설정 가능)
t_input = st.time_input('당신이 태어난 시간은?', step=datetime.timedelta(minutes=10))

st.write(f'이름={txt_input}, 생일={d_input} 시간={t_input}')
