
import streamlit as st
import FinanceDataReader as fdr
import mplfinance as mpf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.subheader('국내 주가 데이터 시각화')

# ======================= 함수 선언부 =========================

# 외부에서 가져오기 때문에 '캐시데이터 설정!!!!!!' 해서 효율적으로 메모리 사용

# 종목 코드 및 기간 설정에 따른 DF 반환 함수
@st.cache_data
def getData(code, dataStart, dateEnd):
    df = fdr.DataReader(code, dataStart, dateEnd)
    return df

# 시가총액 기준으로 종목코드, 회사명 DF 반환 함수
@st.cache_data
def getStockCode(market='KOSPI', sort='Marcap'):
    df = fdr.StockListing(market)   # DF 가져오기
    df.sort_values(by=sort, ascending=False, inplace=True) # 변수명에 바로 반영
    return df[['Code', 'Name']]

# ==============================================================

# ======================= 세션 설정부 =========================

# 종목코드 변경시 목록의 index로 활용될 code_index 키 설정
if 'code_index' not in st.session_state:
    st.session_state['code_index'] = 0

# 기간 설정시 활용될 ndays 키 설정
if 'ndays' not in st.session_state:
    st.session_state['ndays'] = 120

# 차트 스타일 변경시 활용될 'chart_style'키 설정
if 'chart_style' not in st.session_state:
    st.session_state['chart_style'] = 'default'

# 거래량 출력 여부 설정시 활용될 'volume' 키 설정
if 'volume' not in st.session_state:
    st.session_state['volume'] = True

# ===========================================================

# ======================= 사이드바 설정부 =========================

# 사이드바에서 여러 요소들을 입력받아 메인의 차트를 출력할 수 있도록 폼 활용

with st.sidebar.form(key='form1', clear_on_submit=True):
    st.header('🔠 입력값 설정')

    # <종목 선택을 위한 selectbox 만들기>
    # 종목코드와 회사명을 1:1로 매핑시켜서 출력
    choices_tuple = zip(getStockCode()['Code'], getStockCode()['Name'])
    # 보기 좋게 종목코드와 회사명을 ':'로 이어서 한문자열로 리스트에 담기
    choices_list = [' : '.join(i) for i in choices_tuple]  # 만약 값이 숫자면, map으로 감싸서 str로 바꿔서 join 하기~ ':'.join(map(str, i))

    # 매개변수 index : 선택박스의 초기값을 인덱스로 지정(처음에는 세션에 있는 0이 들어가있음) 
    choice = st.selectbox('종목', choices_list, index=st.session_state['code_index'])
    # index 함수: 리스트 내 특정값의 index를 반환 (세션에 반영할 예정)
    code_index = choices_list.index(choice)
    # 종목 코드만 추출 (메인부에서 활용할 예정)
    code = choice.split(' : ')[0]

    # # 확인용~~~~~
    # st.write(choice)
    # st.write(code_index)
    # st.write(code)
    ''

    # <기간 설정 슬라이더 만들기>
    ndays = st.slider('기간 (days): ', min_value=5, max_value=730,
                     value=st.session_state['ndays'], step=1)
    ''

    # <차트 테마 목록 선택박스 만들기>
    chart_style_list = ['binance', 'binancedark', 'blueskies', 'brasil', 'charles',
    'checkers', 'classic', 'default', 'ibd', 'kenan', 'mike', 'nightclouds', 'sas', 
    'starsandstripes', 'tradingview', 'yahoo']
    # index에는 default의 인덱스 번호인 7번 입력 
    chart_style = st.selectbox('차트 스타일: ', chart_style_list, index=7)
    ''

    # <거래량 설정 체크박스 만들기>
    # value=True : 기본으로 체크에 표시되어 있는 상태
    volume = st.checkbox('거래량', value=True)

    # 폼 제출 버튼을 누르면, 세션에 입력값을 업데이트 하고 rerun
    if st.form_submit_button('입력'):
        st.session_state['code_index'] = code_index
        st.session_state['ndays'] = ndays
        st.session_state['chart_style'] = chart_style
        st.session_state['volume'] = volume
        st.rerun()


# ======================================================================

# =========================== 메인화면 설정부 ================================

# 차트 생성 함수 선언
def plotChart(data):
    # 1) 스타일 설정
    chart_style = st.session_state['chart_style']
    marketcolors = mpf.make_marketcolors(up='red', down='blue')
    mpf_style = mpf.make_mpf_style(
        base_mpf_style = chart_style,
        marketcolors = marketcolors
    )
    # 2) 차트 그리기
    fig, ax = mpf.plot(
    data=data,        
    type='candle',
    style=mpf_style,     # 세션 활용
    figsize=(12, 7),
    fontscale=1.0,         
    mav=(5, 20, 60),       
    mavcolors=('green', 'blue', 'orange'),  
    returnfig=True,    
    volume=st.session_state['volume'] # 세션으로 관리 중~~
    )
    return st.pyplot(fig)

# 코스피 종목들 기간 설정 후 getData 실행해서 DF로 반환
date_end = datetime.today().date()
date_start = date_end - timedelta(days=st.session_state['ndays'])
df = getData(code, date_start, date_end) # 사이드바에서 추출한 code 변수 입력

# 현재 저장되어있는 code_index값으로 choices_list에 있는 기업명만 추출하여
# 메인 화면에 종목 타이틀로 지정
# [9:] 앞의 종목코드(6자리)와 ' : '를 빼고 기업명만 슬라이싱
chart_title = choices_list[st.session_state['code_index']][9:]
st.write('현재 차트➡️', chart_title)
st.write('**이동평균선(mav)**: :green[5일], :blue[20일], :orange[60일]')

plotChart(df)
