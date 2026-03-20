
import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory

from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# ========= 추가 =========
from openai import OpenAI
# ========================

st.set_page_config(page_title="AI Assistant", layout="wide")  

load_dotenv()
MY_API_KEY = os.getenv("OPENAI_API_KEY")
chat_model = ChatOpenAI(model='gpt-4o-mini',api_key=MY_API_KEY)

client = OpenAI(api_key=MY_API_KEY)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "사용자의 질문에 대해 이전 질의응답 내용에 기반하여 답변하시오."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ]
)

my_chain = prompt | chat_model

if "pre_memory" not in st.session_state :
    st.session_state.pre_memory = ChatMessageHistory()

if "messages" not in st.session_state :
    st.session_state.messages = [
        {"role": "assistant", 
         "content": """안녕하세요, 저는 이전 대화 내용을 기억하는 AI Assistant입니다.
         무엇을 도와드릴까요?"""}
    ]


@st.cache_resource  # 이 데코레이터가 "한 번 로드한 건 기억해!"라고 명령해요.
def load_my_model():
    model = AutoModelForSequenceClassification.from_pretrained("model/my_RoBERTa_model_naver")
    tokenizer = AutoTokenizer.from_pretrained("model/my_RoBERTa_model_naver")
    return model, tokenizer

# 이제 함수를 호출해서 모델을 가져옵니다. rerun 되어도 다시 안 읽어요!
fine_tun_model, fine_tun_tokenizer = load_my_model()


# ------------------------ 웹 화면 표시부 ------------------------------

st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem !important;  
        padding-bottom: 1rem !important;  
    }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["대화", "감성 분석"])

with tab1 :
    st.header("나의 작고 소중한 GPT 챗봇😊")

    for message in st.session_state.messages :
        with st.chat_message(message["role"]) :
            st.write(message["content"])

    if question := st.chat_input("질문을 입력하세요") :
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user") :
            st.write(question)

        with st.chat_message("assistant") :
            # ============================== 추가 ==============================
            mod_response = client.moderations.create(model="omni-moderation-latest", input=question)
            # 부적절한 내용이 감지된 경우 LLM 체인을 실행하지 않고 차단

            if mod_response.results[0].flagged :
                category_type = dict(mod_response.results[0].categories)
                categories = [cate for cate, TorF in category_type.items() if TorF == True]

                # 안내 메시지 구성
                 # 암시적 문자열 연결 -> ()내에 여러 문자열을 작성하면 하나의 이어진 문자열로 인식
                warning_msg = (
                    "해당 질문은 정책 위반으로 판단되어 필터링 됩니다.\n\n"
                    f"**위반 항목:** {categories}\n\n"
                    "답변 불가합니다. 다른 질문해주세요."
                )
                st.write(warning_msg)

                # 메모리에 차단 내역도 저장
                st.session_state.pre_memory.add_user_message(question)
                st.session_state.pre_memory.add_ai_message(warning_msg)
                st.session_state.messages.append({"role": "assistant", "content": warning_msg})

            # 안전한 질문인 경우 정상적으로 LLM 체인 실행
            else:
                def generate_response() :
                    for chunk in my_chain.stream({
                        "question": question,
                        "chat_history": st.session_state.pre_memory.messages
                    }):
                        yield chunk.content

                answer = st.write_stream(generate_response())

                st.session_state.pre_memory.add_user_message(question)
                st.session_state.pre_memory.add_ai_message(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            # 모든 데이터 저장이 끝났으니, 이제 깔끔하게 순서를 맞추러 갑니다.
        st.rerun()
            # ======================================================================

with tab2 :
    st.header("영화 리뷰 감정 분석 탭🤗")

    input_text = st.text_input('감정을 분석할 텍스트를 입력하세요 :')

    if input_text :
        tokens = fine_tun_tokenizer(input_text, truncation=True, 
                                    padding=True, return_tensors="pt"
                                   )    

        logits = fine_tun_model(**tokens).logits
        #st.write(logits)

        results = torch.softmax(logits , dim=-1)
        #st.write(results)

        pred_classes = results.argmax(-1)

        if st.button(label='텍스트 감성분석 실시~!') :
            if pred_classes[0] == 0 :
                st.write(f"예측 결과 : **부정** 리뷰이며, 확률은 {results[0][0]*100 :.2f}% 입니다.")
            elif pred_classes[0] == 1 : 
                st.write(f"예측 결과 : **긍정** 리뷰이며, 확률은 {results[0][1]*100 :.2f}% 입니다.")

