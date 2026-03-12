import streamlit as st
import time

emp = st.empty() # 빈 좌석 확보
emp.write('empty 예시입니다!') # 그 자리에 앉힘

c1, c2, _, _ = st.columns([1, 1, 1, 4])

start = c1.button('시작', key=1)
clear = c2.button('초기화', key=2)

# start 버튼을 누르면 1초 간격으로 카운트다운 시작
if start:
    with emp:
        for i in range(6):
            cnt = 5-i
            # emp 공간내에서 반복문을 통해 write함수 출력 
            emp.write(f'카운트다운 {cnt}초')      # emp를 써서.... 같은 자리 교체
            time.sleep(1)
        emp.write('empty 내부 카운트다운 실행 완료!!')
    st.write('진짜 끝!')
        # with문 내에서는 emp. 또는 st. 둘 다 사용 가능

# 초기화 버튼을 누를 시
if clear:
    emp.empty() # empty 객체의 내용을 비워줌
    emp.write('empty 예시입니다~!')



## 어제 progress했던..................!
# progress는 진행률만 표현하지만, empty는 글/이미지/바 다ㅏㅏㅏ 가능! 
box = st.empty()
bar = st.empty()

for i in range(101):
    box.write(f"진행률: {i}%")
    time.sleep(0.05)

    bar.progress(i)
    time.sleep(0.05)
