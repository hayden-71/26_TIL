# 지금 이 셀을 py 파일로 저장해줘

import streamlit as st
import pandas as pd

# <타이틀 출력>
st.title('타이틀 - 대')
st.header('타이틀 - 중')
st.subheader('타이틀 - 소')

# <일반 텍스트 출력>
st.text('간단한 텍스트 출력하기~')

# <마크다운 출력>
st.markdown('*마크다운* 출력') # 기울임
st.markdown('**마크다운** 출력') # bold
st.markdown('***마크다운*** 출력') # italic + bold
st.markdown('~~마크다운~~ 출력') # strikethrough(텍스트 중간줄)

# 하이퍼링크적용 
st.markdown('[뉴스 클릭](https://www.topstarnews.net/news/articleView.html?idxno=15945345)')
# 이모지 적용
# 이모티콘 단축 코드 참조: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/
st.markdown('🫶')
st.markdown(':smile: :100: :ocean:')

# <텍스트 및 변수/객체 출력>
st.write('텍스트나 변수 및 객체를 출력')

x, y = 1, 2 # 내부적으로 동작하고, 출력은 안 됨~!
st.write(x, y)
st.write('x=', x, '그리고', 'y=', y) # 포맷팅이 없는 경우 숫자는 초록색으로 출력
st.write(f'x={x} 그리고 y={y}') # 포맷팅이 있는 경우 전체가 다 문자(검은색)으로 출력

# <DataFrame 출력>
df = pd.DataFrame(data={'컬럼1': [1, 2, 3],
                       '컬럼2': ['a', 'b', 'c'],
                       '컬럼3': [True, False, True]
                       })
st.write(df)

# <수식 출력>
st.latex('E= mc^2')                    # ^: 제곱
st.latex(r'Area = \pi r^2 \ 입니다.')   # \pi: 파이
st.latex(r'\frac{a}{b} = c')           # frac{분자}{분모}: 분수
st.latex(r'\sqrt{3}')                 # \sqrt: 제곱근

# <코드 출력>
myCode= '''
total = 0
for i in range(5):
    total += i
print(total)
'''
st.code(myCode)

# <캡션 출력>
st.caption('짧은 설명문(**캡션**) 출력')
