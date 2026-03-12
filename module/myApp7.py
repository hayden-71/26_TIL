
import streamlit as st
# PIL (Python Image Library): 파이썬에서 이미지 처리를 지원하는 라이브러리
from PIL import Image

# camera_input: 카메라 입력받기
# img_input변수는 처음에는 None이다가, Take Photo 버튼을 클릭하면 값이 생김
img_input = st.camera_input('사진 한장 찰칵~! :smile:')
st.write(img_input)

if img_input:
    img = Image.open(img_input)
    st.image(img, width=500)
