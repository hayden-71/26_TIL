
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

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

# fine-tunning 시켜둔 한국어 네이버 영화리뷰 감정분석 모델, 토크나이저 로드
fine_tun_model=AutoModelForSequenceClassification.from_pretrained('model/my_RoBERTa_model_naver')
fine_tun_tokenizer=AutoTokenizer.from_pretrained('model/my_RoBERTa_model_naver')

# ------------------------ 웹 화면 표시부 ------------------------------

st.markdown("""
<style>
.block-container {
    padding-top: 2rem !important;     /* 상단 여백 길이(rem앞의 숫자로 조절) */
    padding-botton: 1rem !important;  /* 하단 여백 길이 */
}
</style>
""", unsafe_allow_html=True)


# =================== 각 기능을 2개의 tab으로 분리 =========================

tab1, tab2 = st.tabs(['대화', '감성 분석'])

with tab1 :
    st.header('나의 작고 소중한 GPT 챗봇 🤓')

    for message in st.session_state.messages :
        with st.chat_message(message['role']) :
            st.write(message['content'])

    if question := st.chat_input('질문을 입력하세요') :
        st.session_state.messages.append({'role':'user', 'content':question})
        with st.chat_message('user') :
            st.write(question)

        with st.chat_message('assistant') :
            def generate_response() :
                # invoke 대신 stream 함수를 사용하여 청크 단위로 받아옴
                for chunk in chain.stream({
                    'question':question, 'chat_history': st.session_state.pre_memory.messages
                }):
                    yield chunk.content 

            answer = st.write_stream(generate_response())


            st.session_state.pre_memory.add_user_message(question)
            st.session_state.pre_memory.add_ai_message(answer)

            st.session_state.messages.append({'role':'assistant', 'content':answer})

with tab2 :
    st.header('영화 리뷰 감정 분석 탭 🎥')

    input_text = st.text_input('감정을 분석할 영화 리뷰 텍스트를 입력하세요 :')

    if input_text :
        # 토큰화
        tokens = fine_tun_tokenizer(input_text, truncation=True, padding=True, return_tensors='pt')

        # 모델로 예측 진행
        logits = fine_tun_model(**tokens).logits
        st.write(logits)

        # softmax로 확률로 변환
        results = torch.softmax(logits, dim=1)  # logits가 2차원이기 때문에
        st.write(results)

        # 최종 정답 클래스 인덱스 (0 또는 1) 출력 -> 0은 부정, 1은 긍정
        pred_classes = results.argmax(-1)

        if st.button(label='텍스트 감정분석 실시!') :
            if pred_classes[0] == 0:
                st.write(f'예측 결과 : **부정 리뷰**이며, 확률은 {results[0][0]*100:.2f}% 입니다.')
            if pred_classes[0] == 1:
                st.write(f'예측 결과 : **긍정 리뷰**이며, 확률은 {results[0][0]*100:.2f}% 입니다.')
