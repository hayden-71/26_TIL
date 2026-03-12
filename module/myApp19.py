import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 메인 타이틀 (중앙쪽에 출력)
_, col, _ = st.columns([1,3,1])
col.header('Iris 데이터 시각화')
''
# iris 데이터 로드
df_iris = sns.load_dataset('iris')

# expander로 데이터 확인 공간 넣기
with st.expander('데이터 확인'):
    # height: DF의 출력 높이 설정
    st.dataframe(df_iris, height=300)

# 사이드바 부분
with st.sidebar:
    sel_x = st.selectbox('x축 특성 선택: ',
                        df_iris.columns[:-1], key=1
                        )
    ''
    sel_y = st.selectbox('y축 특성 선택: ',
                        df_iris.columns[:-1], key=2
                        )
    ''
    # sel_x, sel_y = st.multiselect('x, y축 특성', df_iris.columns[:-1])
    # 이렇게 써도 실행이 되긴 하는데... x, y축 선택할 때 순서를 생각해야 함..

    # 품종은 여러개를 선택할 수 있게 설정
    sel_species = st.multiselect('품종 선택: (:blue[**다중 선택 가능**])',
                                df_iris['species'].unique())
    ''
    # 투명도 설정 (0~1 사이 실수값으로 투명도 설정 가능! 0:투명 / 1:불투명)
    sel_alpha = st.slider('투명도(alpha) 설정:', 0.1, 1.0, 1.0)



# <선택된 값들로 산점도 차트 시각화>
# 품종 유형별로 차트에 표시될 색상을 다르게 지정
colors = {'setosa': 'red', 'versicolor':'blue', 'virginica': 'green'}

# 사용자가 사이드바에서 붓꽃 품종을 선택했을 경우
if sel_species:
    fig = plt.figure(figsize=(7, 5))
    plt.title('Iris Scatter Plot')

    # 사용자가 선택한 특성 및 품종에 따라 산점도 그래프를 반복 출력
    for i in sel_species:
        # 사용자가 선택한 품종 조건에 따라 df를 생성
        df = df_iris[df_iris['species']==i]
        plt.scatter(df[sel_x], df[sel_y],   # x, y축 데이터
           color = colors[i],                # 색상
           alpha = sel_alpha,                 # 투명도
           label = i                         # 점들의 이름, 나중에 legend가 이름을 모아서 표시함!!
           );
    plt.xlabel(sel_x)
    plt.ylabel(sel_y)
    plt.legend()
    st.pyplot(fig)

# 붓꽃의 품종이 선택되지 않았을 경우
else:
    st.warning('🪻 좌측 사이드바에서 품종을 선택해주세요!')
