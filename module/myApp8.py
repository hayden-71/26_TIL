
import streamlit as st
import time

# 진행 바
st.progress(50) # 0~100 사이 정수값

# 움직이는 형태로~~!
# progress_bar = st.progress(0)

# for i in range(0, 101, 10):
#     time.sleep(0.3)          # 일부러 지연
#     progress_bar.progress(i)

# 풍선, 눈송이 효과
# st.balloons()
# st.snow()


# 각종 상태 메시지
st.error('오류 메시지', icon='💸')
st.warning('경고 경고!', icon='🚨')
st.info('공지입니당', icon='👑')
st.success('서ㅇ공~!', icon='🫶')

# with문은 특정 코드 블록의 시작과 끝을 정의해서 그 사이에 원하는 작업을 끝마칠 수 있게 함
# spinner는 실행 중을 표시하는 위젯으로 특정 작업이 진행 중일 때 표시되고, 완료되면 없어져야 함
with st.spinner('실행 중.....'):
    time.sleep(2)
    st.success('종료', icon='✌️')
