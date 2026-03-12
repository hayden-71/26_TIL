import streamlit as st
import pandas as pd

st.title('파일 업로드 & 다운로드 하기')
''
st.subheader('CSV 파일 로드 후 code형태로 출력')
myFile1 = st.file_uploader('1. csv파일 선택: ', type=['csv'], key=1)

with st.container():
    # 파일이 업로드 된다면
    if myFile1:
        st.success('파일 업로드 완료!')
        # myFile1의 내용을 읽어서 디코딩 진행
        code = myFile1.read().decode('utf-8')
        st.code(code)
''
'---'
''
st.subheader('PY(모듈) 파일 로드 후 code형태로 출력')
myFile2 = st.file_uploader('2. py파일 선택: ', type=['py'], key=2)

with st.container():
    if myFile2:
        st.success('파일 업로드 완료!')
        code2 = myFile2.read().decode('utf-8')
        st.code(code2)
''
'---'
''
# CSV 파일 로드 후 데이터프레임으로 출력해보세요
st.subheader('CSV 파일 로드 후 DF로 출력')
myFile3 = st.file_uploader('3. csv 파일 선택: ', type=['csv'], key=3)

with st.container():
    if myFile3:
        st.success('파일 업로드 완')

        # 업로드한 csv 파일을 DF로 출력하기 위해서는 read_csv로 먼저 DF로 받아줘야함 
        df = pd.read_csv(myFile3, encoding='utf-8')
        st.dataframe(df)
''
'---'
''
# 여러개 파일 동시에 올리기
# accept_multiple_files=True : 여러개의 파일을 받을 수 있게 설정
st.subheader('다수의 파일 로드하고 정보 출력')
myFiles = st.file_uploader('4. 다수의 파일 선택:', accept_multiple_files=True)

with st.container():
    if myFiles:
        st.success('다수의 파일 업로드 완')

        # name: myFiles가 가진 파일 이름 반환 함수
        file_names = [i.name for i in myFiles]
        # size : myFiles가 가진 파일 사이즈 반환 함수 (Byte단위로 출력되므로 KB로 변환)
        # :.1f : 실수를 소수점 첫째자리까지만 출력 
        file_sizes = [f'{i.size/1024:.1f}KB' for i in myFiles]

        #join 함수로 데이터를 이어붙여서 출력
        # "구분자".join(문자열 리스트)
        st.write(f'파일이름: {", ".join(file_names)}')
        st.write(f'파일크기: {", ".join(file_sizes)}')
''
'---'
''
# 데이터를 파일로 내려 받기
st.subheader('파일로 다운로드')
df = pd.DataFrame(data={'컬럼1': [1,2,3],
                       '컬럼2': ['a', 'b', 'c'],
                       '컬럼3': [True, False, True]})
st.dataframe(df)

csv_data = df.to_csv(index=False).encode('utf-8-sig')

# 다운로드 버튼 생성
st.download_button(label='위 데이터 파일 내려받기',
                  data=csv_data,
                  file_name='myDF.csv')
