
import streamlit as st
import folium
import streamlit_folium as sf
import numpy as np

# 미니맵 출력 기능, 최대화 창 기능, 히트맵 출력 기능(마커가 많은 곳은 색상이 붉고 진하게 나옴)
from folium.plugins import MiniMap, Fullscreen, HeatMap

st.title('🗺️ Folium - Streamlit 연동')

# 1. 위도, 경도 입력 UI 생성
col1, col2 = st.columns([1, 1])
with col1:
    # 기본 위경도는 서울 시청 값 
    lat0 = st.number_input('위도 입력: ', value=37.55, format='%.2f', step=0.01)

with col2:
    lon0 = st.number_input('경도 입력: ', value=126.99, format='%.2f', step=0.01)


# 2. 지도 스타일 선택
tile_option = st.selectbox(
    '지도 스타일 선택',
    ['OpenStreetMap',
    'CartoDB positron',
    'CartoDB dark_matter',
    'Esri WorldStreetMap',
    'Esri WorldImagery']
)


# 3. 랜덤 마커 시드를 세션으로 관리
if 'seed' not in st.session_state:
    st.session_state['seed'] = 1  # 시드 초기값 숫자는 아무거나 사용해도 됨

if st.button('마커 시드 변경'):
    st.session_state['seed'] += 1  # 여기도 마찬가지. 숫자는 의미가 없음

st.write('현재 시드값:', st.session_state['seed'])


# 4-1. 랜덤 마커값(위도, 경도) 생성 함수 선언
@st.cache_data
def random_markers(n, lat, lon, seed):        # 마커개수, 위도, 경도, 시드값
    np.random.seed(seed)  # 랜덤시드값 고정
    # 원하는 개수만큼 랜덤값을 추가해서 마커 좌표값 생성
    markers = [
        [lat+np.random.randn() / 20, lon+np.random.randn() / 20] for _ in range(n)
    ]

    return markers

# 4-2. 함수 실행하여 랜덤 마커 생성
markers = random_markers(50, lat0, lon0, st.session_state['seed'])
# # <출력 확인용>
# st.write(markers[:3])


# 5. folium 지도 객체 생성
    # location: 초기 중심 좌표값
    # zoom_start: 시작시 줌 배율
    # tiles: 지도 스타일 설정
myMap = folium.Map(location=[lat0, lon0],
                  zoom_start=11,
                  tiles=tile_option)


# 6-1. 마커를 묶어줄 피쳐그룹 객체 생성 (여러 마커들을 묶어서 관리하기 위함)
    # FeatureGroup: 지도 위 여러 요소들을 한 묶음(layer)으로 그룹화
    # add_to: 피쳐그룹 객체의 정보가 표시될 지도 객체 지정
marker_layer = folium.FeatureGroup(name='마커').add_to(myMap)

# 6-2. 여러개의 마커들을 랜덤하게 생성하여 피쳐그룹(marker_layer)에 반복해서 넣기
# location은 [lat, lon] 값 하나만 기대하는데 markers는 좌표 50개 묶음이라 for문 사
popup_cnt = 1
for lat, lon in markers:
    folium.Marker(
        location=[lat, lon],             # 마커가 표시될 위,경도
        popup=f'PopUp_{popup_cnt}',      # 마커 클릭시 출력 팝업 
        tooltip='클릭해보세요!',           # 마커에 마우스 오버시 출력 문구
        icon=folium.Icon(color='blue', icon='star'),  # icon: 마커 출력모양 설정
    ).add_to(marker_layer)               # 해당 마커들을 피쳐그룹에 포함시키기
    popup_cnt += 1


# 7. 히트맵 출력 (마커가 집중된 곳일수록 붉은색)
HeatMap(markers, name='히트맵').add_to(myMap)

# 8. 미니맵, 풀스크린 버튼 설정
MiniMap().add_to(myMap)
Fullscreen().add_to(myMap)

# 9. layer 컨트롤 창 추가 (FeatureGroup이나 Heatmap으로 추가한 layer를 on,off 할 수 있는 창)
folium.LayerControl().add_to(myMap)

# 10. streamlit으로 지도 출력
sf.st_folium(myMap, width=700, height=500, key='main_map')
