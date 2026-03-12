import streamlit as st
import pandas as pd
import numpy as np

st.title('🗺️와아 Streamlit 기본 지도 활용')
st.caption('위도/경도 값을 이용해 지도에 점 찍기📍')

# 1. 슬라이더 위젯으로 데이터의 개수 입력받기
number_of_points = st.slider('표시할 데이터 개수 선택',
                            min_value=1, max_value=200, value=100
                            )

# 2. DF로 데이터 생성
# 서울 시청 좌표 기준
base_lat = 37.5519 # 위도(latitude)
base_lon = 126.9918 # 경도(longitue)

# DF 생성
df = pd.DataFrame({
    # 시청 기준으로 랜덤으로 위 경도 값을 추가
    # 위도, 경도는 숫자가 조금만 바뀌어도 지도에서 멀리 떨어지므로 적당히 50정도로 나눠줌
    'lat': base_lat + np.random.randn(number_of_points) / 50,
    'lon': base_lon + np.random.randn(number_of_points) / 50,
    # 지도에 표시될 점의 크기 결정할 데이터
    'population': np.random.rand(number_of_points) * 300
})

# 3. 데이터 확인용
with st.expander('생성된 위치 데이터 보기'):
    st.dataframe(df)

# 4. 지도 새로고침용 버튼 (데이터가 랜덤이므로 누를때마다 코드 재실행되어 위치 바뀜)
if st.button('데이터 새로고침'):
    st.rerun() # 재실행 (그냥 버튼만으로도 되지만 혹시 몰라서 재실행 기능 넣어줌)

# 5. 지도 출력
st.map(
    df,
    latitude = 'lat', # 위도 (컬럼명 입력)
    longitude = 'lon', # 경도 (컬럼명 입력)
    size= 'population', # 데이터 크기 (컬럼명 입력)
    zoom= 11 # 처음 지도에 보일 확대 정도
)
