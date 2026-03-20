
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

# --------------------------- 사전 설정부 -----------------------------
st.set_page_config(page_title='AI Assistant', layout='wide')

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


if 'pre_memory' not in st.session_state :
    st.session_state.pre_memory = ChatMessageHistory()

if 'messages' not in st.session_state :
    st.session_state.messages = [
        {'role': 'assistant',
        # 첫 대화 전, 화면 접속시 출력되는 문구 설정
        'content': '''안녕하세요! 저는 이전 대화 내용을 기억하는 AI Assistant입니다.
        무엇을 도와드릴까요?'''}
    ]

# ------------------------ 웹 화면 표시부 ------------------------------

st.markdown("""
<style>
.block-container {
    padding-top: 2rem !important;     /* 상단 여백 길이(rem앞의 숫자로 조절) */
    padding-botton: 1rem !important;  /* 하단 여백 길이 */
}
</style>
""", unsafe_allow_html=True) 

st.header('나의 작고 소중한 GPT 챗봇 🤓')

for message in st.session_state.messages :
    with st.chat_message(message['role']) :
        st.write(message['content'])

if question := st.chat_input('질문을 입력하세요') :
    st.session_state.messages.append({'role':'user', 'content':question})
    with st.chat_message('user') :
        st.write(question)

    with st.chat_message('assistant') :
        # ========================= 변경된 부분 ========================
        # 스트리밍 출력을 위한 함수 정의
        def generate_response() :
            # invoke 대신 stream 함수를 사용하여 청크 단위로 받아옴
            for chunk in chain.stream({
                'question':question, 'chat_history': st.session_state.pre_memory.messages
            }):
                yield chunk.content  # 모델이 생성한 토큰 조각을 하나씩 실시간 반환

        # write_stream : 생성되는 토큰을 stream 형식으로 바로바로 앱상에서 출력
        answer = st.write_stream(generate_response())
        # ============================================================

        st.session_state.pre_memory.add_user_message(question)
        st.session_state.pre_memory.add_ai_message(answer)

        st.session_state.messages.append({'role':'assistant', 'content':answer})
