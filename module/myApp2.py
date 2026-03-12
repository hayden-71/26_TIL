
import streamlit as st
import pandas as pd

x, y = 1, 2
df = pd.DataFrame(data={'컬럼1': [1, 2, 3],
                       '컬럼2': ['a', 'b', 'c'],
                       '컬럼3': [True, False, True]
                       })

# 스트림릿의 매직커맨드 활용 (write함수 대신에 아래처럼 작성 가능)
'이것은 **텍스트** 입니다'
x
y
'' # 한줄 공백용으로 사용 가능
''
df

# 마크다운 색상 적용
'마크다운의 :blue[**파란색**] 색상 출력'
'마크다운의 :red[**빨간색**] 색상 출력'
':orange[**귤**은 맛있오]:tangerine:'

# 이모티콘 출력
'헤헷 :sunglasses:'
'하트 :heart:'
'100점 만점에 :100:'
