
import streamlit as st

# <이미지 출력>
'이미지'
st.image('data/냥이.jpg', width=500, caption='점프하는 냥이~~!')

# <음성 출력>
# 음성은 먼저 파일을 불러와서 저장하고 다음에 출력을 진행하는 2단계로 진행
# 'rb'는 읽기 전용으로 파일 불러올 때 사용
# 'wb'는 쓰기 전용으로 파일 내보낼 때 사용
with open('data/clockbell.wav', 'rb') as f:
    audio_data = f.read()
'벨소리'
st.audio(audio_data) # 음성을 웹에 출력

# <영상 출력>
with open('data/wave.mp4', 'rb') as f:
    video_data = f.read()

'ㅠㅏ도영상'
st.video(video_data)


# 오잉 이렇게만 해도 가능한데? 무슨 차이냐!
# 로컬 파일을 재생하거나, 큰 영상일때는 이렇게 쓰는게 효율적임 
# 크롤링/다운로드한 영상/임시파일은 위의 방식으로 '영상 데이터 자체를' 넘는 게 맞음
st.video('data/wave.mp4')
