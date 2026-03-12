import streamlit as st
import requests as req
import time
from streamlit_lottie import st_lottie

# 페이지 기본설정
st.set_page_config(
    page_title='2026 AI Vision',
    page_icon='🚀',
    layout='wide'
)

# lottie 로드 함수 (캐시 적용)
# url 주소에 애니메이션 컨텐츠의 json 주소를 입력하고 출력도 json으로 출력 
@st.cache_data
def load_lottie_json(url):
    res = req.get(url)
    # status_code: <Response [200]>에서 []안의 수치값 확인
    if res.status_code != 200:
        return st.error('통신 에러 발생')
    return res.json()

# 애니메이션 2개에 대해 함수 실행
lottie1 = load_lottie_json(
    "https://lottie.host/b2028fe9-d806-4a8a-8319-7da059ca6504/f10kr05PrR.json"
)
lottie2 = load_lottie_json(
    "https://lottie.host/df90f25b-6928-4a95-9c94-8821d541778c/uhH0uOmErS.json"
)

# 상단 메인 배너
with st.container():
    col1, col2 = st.columns([3, 2])

    # 텍스트 파트 (좌)
    with col1:
        st.title('AI Assistant Service 🤖')
        st.markdown('''
        ### 당신의 업무 효율을 극대화하세요.
        AI 기반의 자동화 솔루션으로 반복 업무는 줄이고,
        **창의적인 일**에 더 집중할 수 있도록 도와드립니다.
        ''')
    # 버튼에 스타일링 넣기
     # type='primary': 중요 버튼(빨간색 배경)으로 시각화
    if st.button('무료 체험 시작하기', type='primary'):
        st.toast('환영합니다. 서비스 체험을 시작합니다. 🎉')

    # 애니메이션 파트 (우)
    with col2:
        if lottie1:
            # height: 애니 높이 (지정하지 않으면 원본 비율로 출력)
            # width: 너비 (지정하지 않으면 할당된 공간에 맞춰 출력)
            st_lottie(lottie1, height=300, key='a')

"---"

# 대시보드 및 목표 설정
st.subheader('📊2026 프로젝트 현황')

col1, col2, col3 = st.columns(3)
col1.metric('현재 사용자', '1,240명', '120명 증가')
col2.metric('AI 모델 정확도', '98.5%', '0.5%')
col3.metric('서버 가동률', '99.9%', '안정적')

# unsafe_allow_html=True : markdown에 HTML 코드 적용 설정
st.markdown('오잉<br>엥', unsafe_allow_html=True) # <br>은 개행 태그

with st.container():
    col1, col2 = st.columns([1, 2])

    # 애니메이션 파트 (좌)
    with col1:
        if lottie2:
            st_lottie(lottie2, height=250, key='b')
    # 텍스트 및 위젝 파트 (우)
    with col2:
        st.markdown('### 🚀2026년, 새로운 도약을 준비하세요!')
        st.write('여러분의 목표를 입력해주시면 AI가 맞춤형 로드맵을 제안해드립니다.')

        user_goal = st.text_input('올해 가장 이루고 싶은 목표는???',
                                  # placeholder: 입력 전 출력되는 옅은 회색 텍스트
                                 placeholder='예: 파이썬 마스터하기, 취업하기, 다이어트 성공하기')

        if st.button('목표 등록'):
            if user_goal:
                # 2초 대기 (현재는 AI는 없고 그냥분석하는 척하기 ^_^)
                with st.spinner('AI가 목표를 분석 중입니다...'):
                    time.sleep(2)
                st.success(f'멋진 목표네요! {user_goal} 달성을 응원합니다!🎁')
                st.balloons()
            else:
                st.warning('목표를 입력해주세요')

'---'
st.markdown('2026 AI Instructor. All rights reserved. | Powered by Streamlit & Lottie')
