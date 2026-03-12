
import streamlit as st
import pandas as pd

df = pd.DataFrame(data={'컬럼1': [1, 2, 3],
                       '컬럼2': ['a', 'b', 'c'],
                       '컬럼3': [True, False, True]
                       })

'1. 매직 커맨드 사용'
df

'2. write 함수 사용'
st.write(df)

'3. dataframe 함수 사용'
st.dataframe(df, width=400)

'4. table 함수 사용'
st.table(df)

st.divider() # 구분선
'---'

# JSON 형식으로 출력
# 웹 통신에서 주로 사용되는 양식으로 여러개의 딕셔너리로 구성됨
st.json([
    {'name': '민정', 'age':20, 'gender':'female'},
    {'name': '민호', 'age':30}
])

'---'

# 데이터 상태 변화 출력
# '숫자 하나 + 변화량을 같이 보여주는 박스'
st.metric(label='온도', value='10℃', delta='2℃')
st.metric(label='삼성전자', value='150,000', delta='-1,000')
