
import streamlit as st
import pandas as pd
import time

# 1. 타이틀 및 부제목
st.title('나만의 작고 소중한 대시보드')
st.header('실습 예제 작성 중!')

# 2. 간단한 텍스트와 마크다운
st.text('이 대시보드는 Streamlit을 활용하여 만들어졌습니다.')
st.markdown('**이곳**에서는 다양한 *Streamlit* 함수를 활용할 수 있습니다. [여기](https://docs.streamlit.io/)를 클릭하여 더 알아보세요.')
'---'
# 3. 데이터프레임과 통계 정보 표시  
df = pd.DataFrame(data={'상품': ['A', 'B', 'C', 'D'],
                       '판매량': [100, 150, 200, 50],
                        '작년대비 증감비': ['+10%', '+5%', '+7%', '-15%']})
df
''
st.metric(label="최대 판매량", value=max(df['판매량']), 
          delta=df[df['판매량']==max(df['판매량'])]['작년대비 증감비'].values[0])

# 다른 풀이!@!!!!!!!!!!!! 
# idx = df['판매량'].idxmax()
# st.metric(label='최대 판매량', value=df.loc[idx, '판매량'], 
#           delta=df.loc[idx, '작년대비 증감비'])

''
# 4. 사용자 입력에 따른 동적 변화
select = st.selectbox(label='어떤 상품의 정보를 보시겠습니까?', options=df['상품'])

st.write(f"{select}의 판매량은 {df[df['상품'] == select]['판매량'].values[0]}입니다.")
''
'---'
''
# 5. 수식 표시
st.latex(r'l = 2\pi r')
''
'---'
''
# 6. 이미지와 캡션
st.image('data/냥이.jpg', width=200, caption='냥이!')
''
'---'
''
# 7. 코드 블록과 경고 메시지
code = '''print('Hello, Streamlit!')'''
st.code(code)
st.warning('이 텍스트는 경고용 메시지 입니다.')
''
'---'
''
# 8. 버튼과 성공 메시지
button = st.button(label='성공 버튼')
if button:
    st.balloons()
    st.write('성공!')
''
'---'
''
# 9. 기타 다양한 입력과 기능 활용
txt = st.text_input('이름을 입력하세요:')
st.write(f'안녕하세요, {txt}님!')
''
'---'
''
c = st.color_picker('색상을 선택하세요')
st.write(f'선택한 색상은 {c}입니다.')
''
'---'
''
# 10. 진행버튼 클릭하면 진행 바가 초당 10%식 차오르도록!
#  - 여러 개의 바가 아닌 하나의 바에서 상태가 업데이트 되어야 함
button = st.button('진행버튼')
if button:
    bar = st.progress(0) # 객체 생
    for i in range(0, 101, 10):
        time.sleep(1)
        bar.progress(i) # “객체.그 객체의 기능(값)”
