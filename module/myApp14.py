import streamlit as st
import time

cont = st.container()
cont.write('container 예시입니다!')

c1, c2, _, _ = st.columns([1, 1, 1, 4])

start = c1.button('시작', key=1)
clear = c2.button('초기화', key=2)

if start:
    with cont:
        for i in range(6):
            cnt = 5-i
            cont.write(f'카운트다운 {cnt}초')
            time.sleep(1)
        cont.write('container 실행 완료!!')

if clear:
    cont.container()
    cont.write('container 예시입니다~!')
