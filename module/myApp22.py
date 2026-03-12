import streamlit as st

st.header('🎈세션 사용법🎈')
st.write('세션에 아무 값도 없는 초기 상태: ', st.session_state)

# session_state 내에 'cnt'라는 키를 만들고 0으로 초기화
# [조건문과 not in을 사용한 이유]
# not in 없이 cnt값을 초기화시키는 코드를 작성하면
# 코드가 재실행 될때마다 이전 입력값을 무시하고 초기값으로 돌아가기 때문에
# 이를 방지하기 위해 첫 시작에만 동작할 수 있게 not in 사용

# 먼저 있나 확인하고 (없으면 만들기)
if 'cnt' not in st.session_state: # 딕셔너리 형태의 저장공간 객체
    st.session_state['cnt'] = 0


# 버튼이 들어갈 컬럼 설정
col1, col2, col3, _ = st.columns([1, 1, 1, 4])

# 증가, 감소, 초기화 버튼
# 버튼을 누르면 버튼에 지정된 key값도 session_state에 추가되며,
# 해당 key값을 가진 버튼을 누르면 value값이 True로 변경됨 
if col1.button('1 증가', key=1):
    st.session_state['cnt'] += 1

if col2.button('1 감소', key=2):
    st.session_state['cnt'] -= 1

if col3.button('초기화', key=3):
    st.session_state['cnt'] = 0

st.write('현재 카운트: ', st.session_state['cnt'])

''
'---'
''

# 폼과 세션 결합
st.header('세션으로 폼 상태 기억하기')

# # 버튼을 눌러서 폼을 보고 싶은 경우
# if st.button('폼 보이기', key=5):
#     with st.form(key='Form1', clear_on_submit=True):
#         name2 = st.text_input(label="**What's your name?**",
#                          placeholder='이름을 입력하세요 ')
#         age2 = st.slider('How old are you?', 1, 100, 30)
#         gender2 = st.radio(label= 'What is your gender?',
#                           options=['남', '여'])

#         if st.form_submit_button('제출하기'):
#             '제출 결과: '
#             st.write({'이름':name2, '나이':age2, '성별':gender2})

# =============================================================
# 버튼이 눌려졌다는 사실을 변수에 저장해두고 버튼이 눌린 상태(True)라면 화면을 보여주게
# 세션으로 그 상태를 관리하도록 코드를 작성

# 폼을 보여줄지 말지를 결정할 'form_open' 값을 세션에 False로 초기화 
if 'form_open' not in st.session_state:
    st.session_state['form_open'] = False

# 폼이 열려있는 상태(True)라면 폼을 보여줌
if st.session_state['form_open']:
    st.subheader('사용자 정보 입력')
    # 폼 생성
    with st.form(key='Form1', clear_on_submit=True):
        name = st.text_input('이름 입력')
        age = st.slider('나이', 20,60,30)
        gender = st.radio('성별', ['남', '여'])

        if st.form_submit_button('제출하기'):
            st.success(f'제출 완료: {age}세, {gender}, {name}님!')

    #폼 닫기 버튼
    if st.button('폼 닫기'):
        st.session_state['form_open'] = False
        st.rerun()

# 폼이 닫혀있는 상태(False)라면 '폼 보이기' 버튼을 보여줌
else:
    st.info('아래 버튼을 누르면 입력 양식이 나타납니다')
    if st.button('폼 보이기'):
        # 버튼을 누르면 세션의 'form_open'이 True가 되어 if문이 실행되게 설정됨
        st.session_state['form_open'] = True
        st.rerun()

