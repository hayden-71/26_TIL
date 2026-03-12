
import folium
import streamlit_folium as sf


# 1. 지도 만들기
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

# 2. '맛집 바구니' (FeatureGroup) 만들기
food_group = folium.FeatureGroup(name='서울 맛집')

# 3. 바구니에 마커 담기
folium.Marker([37.5700, 126.9800], popup='치킨집').add_to(food_group)
folium.Marker([37.5600, 126.9700], popup='피자집').add_to(food_group)

# 4. 바구니 통째로 지도에 넣기
food_group.add_to(m)

# 5. 레이어 껏다 켰다 하는 스위치 추가하기
folium.LayerControl().add_to(m)

sf.st_folium(m, width=700, height=500, key='main_map')
