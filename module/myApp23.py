import streamlit as st
import streamlit_authenticator as stauth
import yaml
import time

# 1. config.yaml 파일 불러오기 (사용자 정보 데이터)
with open('data/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 2. authenticator 객체 생성 (불러온 yaml 파일의 정보를 객체에 입력)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

#  3. 로그인 위젯 생성
authenticator.login(
    # 
    location='main',
    #
    fields={'Form name': '사용자 정보 입력',
            'Username': '사용자 ID',
            'Password': '사용자 PW',
            'Login': '로그인'},
     key = 'login_btn')


# 4. 세션 확인
st.write(st.session_state)
# login 함수 실행시 자독으로 세션에 생성되는 변수들
 # authentication_status: 로그인 상태 변수
 #                      (None: 로그인 전, True: 로그인 성공, False: 로그인 실패)
 # username: 로그인에 성공한 사용자의 ID
 # name: 로그인에 성공한 실제 사용자 이름
 # logout: 로그아웃 상태 변수
 # init: streamlit이 웹과 통신하며 보안을 유지하거나 통계를 내기 위해 사용하는 내부 값


# 5. 로그인 상태에 따른 메인화면 구성
 # 1) 로그인 성공 시
if st.session_state['authentication_status'] : 
    # 로그인후 세션 확인
    # st.write(st.session_state)

    # 환영 문구 및 로그아웃 버튼 배치
    col1, col2 = st.columns([12, 2])

    with col1:
        st.write(f'환영합니다! :blue[**{st.session_state['name']}**]님 🫡')
    with col2:
        # 로그아웃 버튼
        authenticator.logout(
            button_name='로그아웃',
            location='main',
            key='logout_bnt'
        )

    '---'

    st.title('메인 대시보드')
    st.write('여기에 메인 컨텐츠 작성~~!')

# 5.패스워드 변경 기능
    with st.expander('🔒비밀번호 변경하기') :
        try :
            # 변경 폼에 정보를 입력하고 변경을 눌렀을 경우!
            # reset_password : 비밀번호 변경 폼 위젯 생성
            if authenticator.reset_password(
                # 사용자 이름 설정
                st.session_state['username'],
                # 위젯에 보여지는 텍스트 설정
                fields={'Form name':'비밀번호 변경',
                        'Current password':'현재 비밀번호',
                        'New password':'새 비밀번호',
                        'Repeat password':'재입력',
                        'Reset':'변경'
                       },
                key='reset_btn'
            ) :
                # 변경된 비밀번호를 yaml 파일에 저장
                # (다음번 로그인에 변경된 비밀번호가 유지)
                with open('data/config.yaml', 'w', encoding='utf-8') as f :
                    yaml.dump(config, f, sort_keys=False, allow_unicode=True)

                st.success('비밀번호가 변경되었습니다. 다시 로그인해주세요.')

                with st.spinner('2초 후 자동 로그아웃 됩니다.') :
                    time.sleep(2)
                    st.session_state['authentication_status'] = None
                    st.rerun()

        except Exception as e :
            st.error(e)
# Tnstls123.


 # 2) 로그인 실패 시
elif st.session_state['authentication_status'] is False:
    st.error('아이디 또는 비밀번호가 일치하지 않습니다.')

 # 3) 로그인 전 (초기화면) 
elif st.session_state['authentication_status'] is None:
    st.info('로그인이 필요한 서비스입니다.')


