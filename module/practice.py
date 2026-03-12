
import streamlit as st
import requests as req
import time
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import folium
import streamlit_folium as sf


############### 페이지 기본 설정 ###########
st.set_page_config(
    page_title='일단 만드는 중',
    page_icon='🔨',
    layout='wide'
)


################ 사이드바 설정 #############
with st.sidebar:
    col1, col2 = st.columns([10, 5])

    # 로고 부분 (좌측)
    with col1:
        st.image("https://cdn.imweb.me/upload/S20210809c06cc49e8b65a/e80edc05fd91a.png",)
    # 텍스트 부분 (우측)
    with col2:
        st.markdown('### 지금 **집** 가고 싶은 사람?')

    st.radio('진짜 솔직히 대답하기', ['저요', '나', '모두 같은 마음'])


    option_menu_side = option_menu(
        menu_title='효율적으로 집 가는 법',      
        menu_icon='house-fill',        
        options=['걸어가기', '대중교통 이용하기', '순간이동'], 
        icons=['person-walking', 'bus-front', 'arrow-up-circle-fill'], 
        default_index=0,   
        styles={
            'container':{'padding':'2!important','background-color':'#fafafa'},
            'icon': {'color':'black', 'font-size':'18px'},
            'nav-link': {'font-size':'15px', 'text-align': 'left', 'margin':'1px',
                        '--hover-color': '#eee'},
            'nav-link-selected': {'background-color':'gray'}
        }
    )

    st.info(f'현재 접속: {option_menu_side} 모드')

if option_menu_side == '걸어가기':
    st.title('🚶‍➡️뚜벅뚜벅 걸어가기🚶')

    option_menu_main = option_menu(
        menu_title=None, # 메뉴 타이틀 숨기기 
        options=['집 찾기', '실시간 트래픽'],
        icons=['card-checklist','activity'],
        default_index=0,
        orientation='horizontal', # 메뉴 탭 출력 형태를 수평으로 설정 (수직은 vertical)
        styles={
            'container':{'padding':'1!important', 'background-color':'#E8E8E8'},
            'icon':{"color": "#000",'font-size':'15px'},
            'nav-link':{'font-size':'15px', "text-align": "center", 'margin':'1px',
                       '--hover-color': '#eee'},
            'nav-link-selected': {'background-color': 'red'}
        }
    )
    if option_menu_main == '집 찾기':
        # 맵 넣어주기
        myHome = folium.Map(location=[37.5665, 126.9780], zoom_start=13)
        # 경로 (이미 계산된 좌표라고 가정)
        route = [
            [37.5665, 126.9780],
            [37.5651, 126.9895],
            [37.5700, 127.0000]
        ]
        # 경로 그리기
        folium.PolyLine(route, color="blue", weight=5).add_to(myHome)
    sf.st_folium(myHome, width=700, height=500, key='map')

# 대중교통
if option_menu_side == '대중교통 이용하기':
    st.title('🚌')
    # 버스, 지하철 고르기
    # 지역 고르기
    # 실시간 버스 노선, 지하철 노선 보여주기

if option_menu_side == '순간이동':
    st.title('☝️순간이동 가보자고')


    # 이미지 가져오기
    @st.cache_data
    def load_lottie_json(url):
        res = req.get(url)
        # status_code: <Response [200]>에서 []안의 수치값 확인
        if res.status_code != 200:
            return st.error('통신 에러 발생')
        return res.json()

    # 애니메이션 2개에 대해 함수 실행
    lottie2 = load_lottie_json(
        "https://lottie.host/9a496984-15ab-4bda-99dd-345087743117/gnkgEi2Vv3.json"
    )

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            if lottie2:
                st_lottie(lottie2, height=250, key='b')
        with col2:
            st.markdown('## 오늘도 고생하셨습니다!')
            st.write('지금 당장 당신의 집으로 향하세요! ☝️🏠')

            if st.button('집 가는 버튼', type='primary'):
                with st.spinner('향하는 중...'):
                    time.sleep(2)
                st.warning('그런 건 없습니다. 길 미끄러우니 조심히 가세요..')

'---'
st.caption('ⓒ 2026 How to go home | Powered by Streamlit & Lottie')
