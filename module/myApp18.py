import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# 차트 한글 설정
from matplotlib import rc
rc('font', family='Malgun Gothic') # 맥은 AppleGothic

# set_page_config: 화면 전체 레이아웃 설정 (Streamlit UI 코드들 앞(윗쪽)에 나와야 함)
st.set_page_config(
    page_title = '내 데이터 분석 앱', # 브라우저 탭 제목
    page_icon = '📊',              # 브라우저 탭 아이콘
    layout = 'wide',               # centered(기본), wide(꽉 차게)
    initial_sidebar_state = 'expanded'
    # 사이드바 조절 (auto:자동, expanded: 열어둔 채로 시작, collapsed: 닫은채로 시작)
)

st.title('💻 Streamlit - matplotlib, seaborn 연동')
st.write('wide 모드로 설정하면 화면 양옆 여백없이 활용 가능!')
st.sidebar.title('여기는 사이드바!!')

# 데이터 로드
df = pd.read_csv('data/train.csv', encoding='euc-kr')
'데이터 출력'
st.dataframe(df.head())
''
'---'
''
# 1. matplotlib의 bar 차트 출력
st.subheader('1. matplotlib 차트 출력')
vc = df['Survived'].value_counts()    # Survived: 생존여부 컬럼 (0 or 1)
fig1 = plt.figure(figsize=(4, 3))
plt.bar(vc.index, vc.values)         # bar 차트 생성 (x축에는 index, y축에는 실제값)
plt.title('타이타닉 생존 데이터')
plt.xticks(np.arange(2), ['사망', '생존'])
st.pyplot(fig1)        # streamlit의 pyplot 함수(차트 출력)에 figure객체를 넣어줘야 함

''
# 2. seaborn의 countplot 차트 출력
st.subheader('2. seaborn 차트 출력')
fig2 = plt.figure(figsize=(5, 3))
# countplot: 데이터의 종류별 개수를 막대 그래프로 출력
sns.countplot(data = df,
             x = 'Pclass',     # x축 칼럼(컬럼 내부의 유니크 값들이 각각 들어감)
             hue = 'Embarked'  # x축에 따라 y축 개수가 표시될 컬럼(범례도 자동 출력)
             )

plt.title('Pclass(객실등급)에 따른 탑승지 분포')
st.pyplot(fig2)
''
'---'
st.subheader('3. 히스토그램을 활용한 나이대별 생존자 분포 출력')
fig3 = plt.figure(figsize=(5, 3))
sns.histplot(data=df,
            x='Age',
            hue='Survived',
            bins=30,     # 구간의 개수 (30개로 나눔)
            kde=True     # 부드러운 곡선을 겹쳐서 보여주게 설정 
            )
plt.title('나이에 따른 생존/사망 분포')
st.pyplot(fig3)
''
'---'
# 4. seaborn 차트를 객체지향 방식으로 출력
# figure와 axes(축)객체를 명시적으로 다뤄서 좀 더 복잡하지만, 구조화된 레이앙웃 설정에 좋음
st.subheader('4. subplot을 활용한 여러 차트 출력')
# subplots: 단일 공간에 여러개의 차트를 생성 (매개변수로 행, 열 개수 및 figsize 등 지정 가능)
fig4, ax = plt.subplots(2, 2, figsize=(8,6))
# fig4: 그래프 객체, ax: 축 객체

# 좌상단 subplot
sns.countplot(data=df, x='Pclass', hue='Embarked', ax=ax[0,0])
ax[0,0].set_title('객실 등급별 탑승 지역 수', fontsize=10)
ax[0,0].legend(loc='upper left', prop={'size': 5})

# 우상단 subplot
sns.countplot(data=df, x='Pclass', hue='Survived', ax=ax[0,1])
ax[0,1].set_title('객실 등급별 생존/사망자 수', fontsize=10)
ax[0,1].legend(loc='upper right', prop={'size': 5})

# 좌하단 subplot
sns.countplot(data=df, x='Sex', hue='Embarked', ax=ax[1,0])
ax[1,0].set_title('성별 별 탑승 지역 수', fontsize=10)
ax[1,0].legend(loc='lower left', prop={'size': 5})

# 우하단 subplot
sns.histplot(data=df, x='Age', hue='Survived', bins=10, ax=ax[1,1])
ax[1,1].set_title('나이대 별 생존/사망자 수', fontsize=10)

plt.tight_layout() # 차트간 거리 자동 간격 조정
st.pyplot(fig4)
