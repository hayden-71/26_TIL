import streamlit as st
import json
import requests
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from PIL import Image
from bs4 import BeautifulSoup as bs


# ========================= 함수 선언부 ==========================
# 네이버 뉴스 검색 결과를 반환하는 함수
def getRequest(keyword, display, start) : # 키워드, 검색량, 시작점
    url = f'https://openapi.naver.com/v1/search/news.json?query={keyword}&display={display}&start={start}'
    N_A = {'X-Naver-Client-Id': st.session_state['client_id'], 
           'X-Naver-Client-Secret': st.session_state['client_secret']}
    res = requests.get(url, headers=N_A) # 통신 요청
    my_json = json.loads(res.text) # json 형식으로 파싱

    return my_json['items']

# 워드클라우드 시각화 함수
# (문자열 텍스트, 배경 이미지, 최대 단어수, empty공간 객체)
def wcChart(corpus, back_mask, max_words, emp) :
    # 배경 이미지 선택
    if back_mask == '타원':
        img = Image.open('data/background_1.png')
    elif back_mask == '말풍선':
        img = Image.open('data/background_2.png')
    elif back_mask == '하트':
        img = Image.open('data/background_3.png')
    else :
        img = Image.open('data/background_0.png')

    # 배경 이미지를 배열로 변환
    my_mask = np.array(img)

    # 워드 클라우드
    wc = WordCloud(
    font_path=r'C:\Windows\Fonts\Gulim.ttc', 
    background_color='white',
    max_words=max_words,               
    random_state=99,            
    stopwords=['있다', '및', '수', '이', '다', 'the', 'a', 'of', 'to', 'in', 'and'],   

    mask=my_mask,       
    contour_color='black',  
    contour_width=3
)

    wc.generate(corpus)   # 함수의 매개변수인 corpus 입력
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(fig)
    # 함수의 매개변수인 emp 입력
    emp.info(':orange[**워드클라우드 이미지 생성 완료**]', icon='👍')
# ==============================================================
# ========================= 세션 설정부 ==========================

if 'client_id' not in st.session_state:
    st.session_state['client_id'] = ''

if 'client_secret' not in st.session_state:
    st.session_state['client_secret'] = ''


# ==============================================================
# ======================== 사이드바 부분 =========================

with st.sidebar.form(key='form1', clear_on_submit=False):
    st.header('네이버 API 설정💌')

    client_id = st.text_input('Client ID:', value=st.session_state['client_id'])
    client_secret = st.text_input('Client Secret:', 
                                  type='password',
                                  value=st.session_state['client_secret'])

    if st.form_submit_button(label='Ok'):
        st.session_state['client_id'] = client_id
        st.session_state['client_secret'] = client_secret
        st.write('연결 완료')

# ==============================================================
# ========================== 메인 부분 ==========================

# 진행상황 문구를띄워줄 빈 공간 객체 설정
chart_emp = st.empty()

try :
    with st.form(key='form2', clear_on_submit=False) :
        search_keyword = st.selectbox(
            # 뉴스 대표 카테고리들
            '키워드 :', ['핀테크', '경제', '정치', '국제', '연예', 'IT', '문화']
        )

        data_amount = st.slider(
            '분량(1당 100개) :', min_value=1, max_value=5, value=1, step=1
        )

        back_mask = st.radio(
            '워드클라우드 출력 형태 :', ['기본', '타원', '말풍선', '하트'],
            horizontal=True   # 수평 출력
        )

        if st.form_submit_button('출력') :
            chart_emp.info(':red[데이터 수집 중...]', icon='😉')
            items = []    # 뉴스 기사 정보가 담길 리스트
            corpus = ''   # 수집된 뉴스 본문 문자열이 담길 변수

            # 수집 데이터의 양 설정(입력받은 data_amount만큼 반복하여 빈 리스트에 기사 정보 넣기)
            for i in range(data_amount) : 
                # 기사 정보를 수집하는 getRequest 함수 실행(키워드, 한번에 표시될 양, 시작 시점)
                items.extend(getRequest(search_keyword, 100, 100*i+1))

            for item in items :
                # 뉴스 링크가 네이버 링크라면
                if 'n.news.naver' in item['link'] :
                    # 뉴스 url 저장
                    news_url = item['link']   
                    # 통신 요청
                    res = requests.get(news_url, headers={'User-Agent':'Mozilla'})
                    # BS 파싱
                    soup = bs(res.text, 'lxml')
                    # 뉴스 본문 영역에 접근
                    news_tag = soup.select_one('#dic_area')
                    # 텍스트만 추출하여 빈 문자열에 계속 넣어주기
                    corpus += news_tag.text + '\n'

            st.markdown(f'**수집된 corpus 길이** : {len(corpus)}')

            # 워드클라우드를 출력하기에 충분한 데이터가 확보되었으면 시각화 출력
            if len(corpus) >= 300 :    # 300자 이상일 경우
                chart_emp.info(':red[이미지 생성중...]', icon='✌️')
                # 워드클라우드 생성 함수 실행
                wcChart(corpus, back_mask, 100, chart_emp)
            else :
                chart_emp.error(':red[워드클라우드를 생성하기에 데이터가 충분하지 않습니다.]')

except Exception as e :
    st.write(e)
    chart_emp.error('ID와 Secret을 입력해주세요')




# ==============================================================
