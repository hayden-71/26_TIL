import streamlit as st
import pandas as pd
import numpy as np

# 랜덤한 데이터로 DF 생성
data = np.random.randn(20, 3) # (행, 열)
df = pd.DataFrame(data, columns=['가', '나', '다'])

with st.expander("df를 열어보세용"):
    st.dataframe(df)

# 라인/영역/바 차트
'라인차트 시각화 결과 ↓👇↓👇↓'
st.line_chart(df, x_label='No', y_label='value')

'영역차트 시각화 결과 👇↓👇↓'
st.area_chart(df, x_label='No', y_label='value')

'바차트 시각화 결과 👇👇'
st.bar_chart(df, x_label='No', y_label='value')

''
'---'
''
############## DF 내부에 차트 그리기 ################
st.write('데이터프레임 내부 시각화 😽')

data={
    '이름':['a지점', 'b지점', 'c지점'],
    '주간매출추이': [
        [10, 20, 30, 15, 40],
        [50, 30, 20, 10, 5],
        [20, 20, 30, 30, 50]
    ],
    '총매출': [1250, 500, 3500]
}

df2 = pd.DataFrame(data)
st.dataframe(
    df2,

    # column_config: 데이터프레임의 특정 컬럼을 어떻게 보여줄지 정의하는 설정.
    # DF를 단순한 표가 아니라 풍부한 시각적 대시보드로 만들어줌
    column_config={
        # '이름'은 실제 DF에 있는 컬럼명
        '이름': st.column_config.Column(
            '지점명', # 웹상의 DF에 출력할 컬럼명
            width='small'), # 컬럼 너비(small, medium, large 혹은 점수 입력)


        # LineChartColumn: 컬럼 내에 작은 라인 차트 (시간에 따른 변화 추세를 볼 때 사용)
        # 스파크라인 차트라고도 부르며 축이나 라벨이 없는 작은 차트 형태
        '주간매출추이':st.column_config.LineChartColumn(
            '주간 매출 추이',
            width='medium',
            help='지난 5주간의 매출변화입니다.', # 마우스 오버시 출력 텍스트
            y_min=0, y_max=50), # y축의 최소, 최대값 설정

        # ProgressColumn: 컬럼 내의 작은 진행 바 (달성률, 점수 등 단일값의 크기를 볼 때)
        '총매출':st.column_config.ProgressColumn(
            '총 매출액',
             width='medium',
            help='현재까지의 누적 매출',
            format='$%d', # 출력 형식 지정 (%.2f로 하면 1250.00으로 출)
            min_value=0, # 바의 최소값
            max_value=4000) # 바의 최대값 설정

    },
    hide_index=True # 출력 DF에 인덱스 컬럼 숨기기
)
