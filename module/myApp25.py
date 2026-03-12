
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu

# 페이지 기본 설정
st.set_page_config(
    layout='wide',
    page_title='AI Dashboard',
    page_icon='📉'
)

# === [사이드바 부분] ===
with st.sidebar:
    col1, col2 = st.columns([1, 5])

    # 로고 부분 (좌측)
    with col1:
        st.image("https://slack-imgs.com/?c=1&o1=ro&url=https%3A%2F%2Fcdn-icons-png.flaticon.com%2F512%2F2103%2F2103633.png", width=50)
    # 텍스트 부분 (우측)
    with col2:
        st.markdown('### AI Control Center')

    #사이드바에 option_menu UI 배치
    option_menu_side = option_menu(
        menu_title='메뉴 선택',                   # 메뉴 박스 이름
        menu_icon='cast',                        # 이름 앞에 붙는 아이콘
        options=['대시보드', '데이터 분석', '설정'],  # 메뉴 탭 명칭들
        icons=['speedometer2', 'bar-chart-line', 'gear'], # 탭 앞에 붙는 아이콘
        default_index=0,       # 앱 실행시 가장 먼저 선택되어 있을 메뉴의 인덱스 번호
        styles={
            # container : 메뉴 탭들을 감싸는 전체 공간
            # padding : 요소 내부의 여백 (현재는 0으로 여백 없으며, !important는 해당스타일 우선 적용)
            # background-color : 배경색 (컬러 HEX코드 값으로 설정 가능하며 컬러명 문자로도 가능)
            'container':{'padding':'0!important','background-color':'#fafafa'},
            # 아이콘 세부 사항 설정
            'icon': {'color':'orange', 'font-size':'18px'},
            # nav-link: 메뉴 탭 내부 관련 설정
            # text-alignL 텍스트 정렬
            # margin: 메뉴 탭 가싸고 있는 박스와 텍스트 사이 공간
            # --hover-color: 메뉴에 마우스 오버시 변경되는 색상 (#eee 옅은 회색)
            'nav-link': {'font-size':'16px', 'text-align': 'left', 'margin':'0px',
                        '--hover-color': '#eee'},
            # nav-link-selected: 메뉴 탭이 선택되었을 때 설정 (#02ab21은 진한 녹색)
            'nav-link-selected': {'background-color':'#02ab21'}
        }
    )

    st.info(f'현재 접속: {option_menu_side} 모드')


# === [메인 부분] ===
# 1) 대시보드 선택 시
if option_menu_side == '대시보드':
    st.title('🚀대시보드')

    option_menu_main = option_menu(
        menu_title=None, # 메뉴 타이틀 숨기기 
        options=['요약 보기', '실시간 트래픽', '보고서 다운로드'],
        icons=['card-checklist','activity', 'cloud-download'],
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
    '---'
    # 메인 메뉴 요약보기 눌렀을 때
    if option_menu_main == '요약 보기':
        # KPI 지표 카드 예시
        col1, col2, col3 = st.columns(3)
        col1.metric('총 방문자', '12,450명', '▲ 15%')
        col2.metric('매출액', '$54,000', '▲8%')
        col3.metric('서버 상태', '정상', '99.9%')

        st.success('오늘의 주요 지표 현황입니다.')

    elif option_menu_main == '실시간 트래픽':
        st.subheader('📊실시간 접속 현황')
        # 더미 차트 생성
        chart_data = pd.DataFrame(np.random.randn(20,3),
                                 columns=['A', 'B', 'C'])
        st.line_chart(chart_data)

    elif option_menu_main == '보고서 다운로드':
        st.warning('🔒 관리자 권한이 필요합니다.')
        with st.empty(): 
            if st.button('권한 요청하기'):
                st.success('권한이 요청되었습니다.')

# 2) '데이터 분석' 선택 시
if option_menu_side == '데이터 분석':
    st.title('📉데이터 탐색기(EDA)')
    tab1, tab2 = st.tabs(['📁파일 업로드', '🔎데이터 미리보기'])
    with tab1:
        st.file_uploader('분석할 CSV 파일을 업로드하세요~!', type=['csv', 'xlsx'])
    with tab2:
        st.write('업로드된 데이터가 없습니다. 아래는 샘플 데이터입니다~~')
        st.dataframe(pd.DataFrame({'모델':['A', 'B'], '정확도':[0.95, 0.88]}))

# 3) '설정' 선택 시
if option_menu_side == '설정':
    st.title('⚙️환경설정')
    # toggle: on, off 설정 위젯
    st.toggle('다크 모드 적용')
    # value=True : 처음부터 on 상태
    st.toggle('알림 받기', value=True)

    st.markdown('### 사용자 정보')
    # type='password': 입력값이 보이지 않게 설정
    st.text_input('Password 입력', type='password')

    if st.button('저장하기'):
        # toast: 잠깐 떴다가 사라지는 인스턴ㄴ트 알림 메시지
        st.toast('설정이 저장되었습니다!', icon='✅')
