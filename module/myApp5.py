
import streamlit as st

# 버튼 위젯 (같은 label로 버튼을 만들면 오류가 생겨서, key를 다르게 설정해줘야 함!)
st.button(label='클릭!', key=1)

# 버튼이 눌려질 때 py 파일의 코드(스크립트)는 재실행이 됨
# (위젯으로 이벤트를 주게 되면, 웹에서 통신이 발생하고 최신 UI를 출력하기 위해서는
# 코드에 변경이 있는 부분을 다시 알려줘야 하기 때문에 스크립트를 다시 한 번 전달해서 요청함)

# help: 버튼에 마우스 오버시 출력시켜주는 툴팁 
st.button(label='클릭!', key=2, help='이것은 :blue[**툴팁!**]')


# 버튼이 눌러졌을 때 동작할 함수 선언
def myFunc(*args):
    total = 0
    for i in args:
        total += i
    st.write(f'합계 : {total}')

# on_click: 버튼을 눌렀을 때 동작할 함수 지정
# args: 함수의 매개변수에 들어갈 값 지정. 개수 상관없음!!!!!!! 
st.button('클릭!', key=3, on_click=myFunc, args=range(1, 4))


# 버튼 눌렀을 때 동작할 코드를 조건문으로 작성
button = st.button('클릭!', key=4)
st.write(button)

if button:
    st.write(':smile:')
else:
    st.write(':sunglasses:')

''
'---'
''

# 체크 박스 (웹 UI에서 체크를 하면 True 로 값이 바뀜)
temp = st.checkbox('위 내용에 동의합니다!')
st.write(temp)


''
'---'
''

# 라디오 박스 ()
# <참고> 위젯의 종류가 달라도 key 값이 같으면 에러 발생
radio = st.radio(label='다음 중 한 가지 선택', options=['부먹', '찍먹'], key='a')
st.write(f'**radio 선택 =** {radio}')

''
'---'
''

# 선택 박스 (여러개의 값 중 하나 선택)
select = st.selectbox(label='다음 중 한가지 선택', options=['물복', '딱복'])
st.write(f'**selectbox 선택 =** {select}')

''
'---'
''

# 다중 선택 박스 (여러개의 값을 동시에 선택 가능)
mul_sel = st.multiselect('저메추 받습니다?!', ['소고기', '치킨', '마라탕', '엽떡'])
st.write(f'**multi sel 선택 =** {mul_sel}')

''
'---'
''

# 컬러 선택 (컬러는 변수 출력시 HEX 컬러코드 값으로 출력됨)
# HSL : Hue(색상), satuation(채도), ligthness(명도)
c = st.color_picker('컬러 선택')
st.write(f'**color picker 선택 =** {c}')
