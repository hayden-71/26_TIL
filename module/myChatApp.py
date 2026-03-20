
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

# --------------------------- 사전 설정부 -----------------------------
st.set_page_config(page_title='AI Assistant',
                  layout='wide'
                  )

load_dotenv()
MY_API_KEY = os.getenv('OPENAI_API_KEY')
chat_model = ChatOpenAI(model = 'gpt-4o-mini', api_key=MY_API_KEY)

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', '사용자의 질문에 대해 이전 질의응답 내용에 기반하여 답변하시오.'),
        MessagesPlaceholder(variable_name='chat_history'),
        ('human', '{question}')
    ]
)

chain = prompt | chat_model


# 히스토리 객체는 이전 대화 내용을 계속 기억하고 유지해야하기 때문에 session으로 관리
if 'pre_memory' not in st.session_state :
    st.session_state.pre_memory = ChatMessageHistory()

# 화면에 표시되는 대화 내역을 session으로 관리
if 'messages' not in st.session_state :
    st.session_state.messages = [
        {'role': 'assistant',
        # 첫 대화 전, 화면 접속시 출력되는 문구 설정
        'content': '''안녕하세요! 저는 이전 대화 내용을 기억하는 AI Assistant입니다.
        무엇을 도와드릴까요?'''}
    ]


# --------------------------------------------------------------------
# ------------------------ 웹 화면 표시부 ------------------------------
# 전체 페이지 위아래 공백 조정
st.markdown("""
<style>
.block-container {
    padding-top: 2rem !important;     /* 상단 여백 길이(rem앞의 숫자로 조절) */
    padding-botton: 1rem !important;  /* 하단 여백 길이 */
}
</style>
""", unsafe_allow_html=True)        # html 코드로 동작하게 설정


st.header('나의 작고 소중한 GPT 챗봇 🤓')

# session에 있는 messages 값들 중 하나씩 가져와서 반복
for message in st.session_state.messages :
    # chat_message : role에 따른 채팅 UI 설정 함수 (user와 assistant가 다르게 설정됨)
    with st.chat_message(message['role']) :
        st.write(message['content'])

    # 사용자의 입력 처리
    # := 바다코끼리 연산자! 변수 대입과 동시에 그 값을 반환하는 연산자
    # question = st.chat_input('질문을 입력하세요')
    # if question :
if question := st.chat_input('질문을 입력하세요') :
    # session의 messages에 사용자 질문 추가
    st.session_state.messages.append({'role':'user', 'content':question})
    # 화면에 사용자 질문 표시
    with st.chat_message('user') :
        st.write(question)

    # 모델 응답 표시
    with st.chat_message('assistant') :
        response = chain.invoke({
            'question': question,
            # session의 pre_memory에서 메세지를 불러와서 chain 호출
            'chat_history': st.session_state.pre_memory.messages
        })

        answer = response.content
        st.write(answer)

        # 히스토리 업데이트
        st.session_state.pre_memory.add_user_message(question)
        st.session_state.pre_memory.add_ai_message(answer)

        # session의 messages에 모델의 응답도 추가 (출력용)
        st.session_state.messages.append({'role':'assistant', 'content':answer})
