import os
from dotenv import load_dotenv
import asyncio

# List: 리스트  객체 생성 (리스트에 특정 자료형만 들어오게 설정 가능)
# Literal : 반환 문자열 고정 클래스 (변수나 함수의 반환값이 지정한 단어/문자열들 중 하나만 나와야 하는 경우 사용)
from typing import Annotated, TypedDict, List, Literal

### pydantic : LLM의 자연어 응답을 정확한 양식(JSON)으로 정제해주는 라이브러리
# BaseModel : 클래스 생성시 데이터 유효성을 검사하는 클래스
# (langchain은 BaseModel을 상속받은 클래스의 구조를 분석하여 LLM이 이해할 수 있는 JSON형식으로 자동 변환)
# Field : BaseModel 내부의 각 속성에 대해 추가적인 메타데이터를 제공하고 데이터 제약 조건을 세밀하게, 유연하게 설정
from pydantic import BaseModel, Field

from langchain_anthropic import ChatAnthropic

# Upstage 문서 파싱 API 클래스 (일반 문서 로더들보다 성능이 좋음)
from langchain_upstage import UpstageDocumentParseLoader

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

# ====================================================
# 1. 상태(state) 및 각 에이전트 출력 형식 정의
# ====================================================


# 1) 상태 정의
class InterviewState(TypedDict):
    messages: Annotated[list, add_messages]
    applicant_name: str  # 지원자 이름
    resume_content: str  # 이력서 내용
    keywords: List[str]  # 핵심 키워드 (문자열만 받는 리스트로 정의)
    question_count: int  # 질문 횟수
    is_finished: bool  # 면접관과 에이전트가 스스로 판단하는 종료 플래그
    evaluator_result: str  # 평가 결과
    evaluator_reason: str  # 평가 이유
    final_decision: str  # 인사담당자의 최종 승인 플래그


# 2) 인사담당자 에이전트용 출력양식 지정 (BaseModel 클래스 상속)
class HRAnalysis(BaseModel):
    applicant_name: str = Field(description="이력서에서 추출한 지원자 이름")
    keywords: List[str] = Field(
        description="면접에 활용할 수 있는 핵심 기술/경험 키워드 3~5개"
    )


# 3) 면접관 에이전트용 출력양식 지정
class InterviewerAction(BaseModel):
    question: str = Field(
        default="", description="지원자에게 던질 꼬리 질문 (종료시 빈 문자열)"
    )
    # 면접을 종료할 때는 질문을 더 만들지 않도록 default값으로 빈 문자열 부여
    # (pydantic으로 변수를 선언했는데 사용하지 않으면 에러가 발생하기 때문)
    is_finished: bool = Field(
        description="충분히 검증되어 질문을 그만하고 평가자에게 넘길거면 True, 아니면 False"
    )


# 4) 평가자 에이전트용 출력양식 지정
class EvaluatorResult(BaseModel):
    status: Literal["PASS", "FAIL"] = Field(
        description="최종판정 (반드시 PASS 또는 FAIL)"
    )
    reasoning: str = Field(description="합격/불합격으로 판단한 결정적 사유 3문장 이내")


# ====================================================
# 2. 함수 & LLM 세팅
# ====================================================
def send_final_email(applicant_name: str, result: str) -> None:
    """최종 결정에 따라 합/불 안내 이메일을 발송합니다."""
    print(f"\n[메일 시스템 가동] 수신자: {applicant_name} 지원자님")
    if result == "PASS":
        print("내용: 축하합니다! AI 면접 전형에 '최종합격'하셨습니다. \n")
    else:
        print("내용: 안타깝게도 이번 전형에서는 모시지 못하게 되었습니다.")


llm = ChatAnthropic(
    model="claude-sonnet-4-6", temperature=0.2, api_key=ANTHROPIC_API_KEY
)


# ====================================================
# 3. 노드 정의
# ====================================================


# 1) HR 시작 노드 (면접을 처음 시작할 때)
async def hr_start_node(state: InterviewState):
    print("[HR 담당자] Upstage API로 이력서를 분석합니다...")

    file_path = "mcpServer/김민정_DBA_이력서.pdf"
    loader = UpstageDocumentParseLoader(
        file_path,
        api_key=UPSTAGE_API_KEY,
        # 로드한 문서를 분리할 단위 설정
        # "None" : 문서 전체를 하나의 Document 객체로 반환
        # "element" : 의미있는 레이아웃 요소 (문단, 표, 제목 등)으로 반환
        # "page"
        split="element",
        # 출력 텍스트 형식 지정
        # "html" : HTML 태그로 감싸서 반환
        # "text" : 순수 텍스트로 바환
        # "markdown" (LLM이 이해하기 쉬움)
        output_format="markdown",
    )

    resume_text = "\n".join([doc.page_content for doc in loader.load()])

    prompt = f"""다음 이력서를 분석하여 지원자 이름과 면접용 핵심 키워드를 추출하세요.
    [이력서]
    {resume_text}
    """

    # analysis 변수에 HRAnalysis 클래스에 정의된 규격에 맞는 데이터만 들어가도록 함
    # with_structured_output : 특정 에이전트의 JSON 형식에 맞춰서만 응답하도록 지시
    # ainvoke : 비동기 응답 실행
    analysis: HRAnalysis = await llm.with_structured_output(HRAnalysis).ainvoke(
        [HumanMessage(content=prompt)]
    )

    # 실제로 analysis 변수에는 아래 형태로 HRAnalysis 객체 자체가 저장됨
    # HRAnalysis(applicant_name="김민정", keywords=["python", "Langchain"])

    print(
        f" -> [추출 완료] 지원자: {analysis.applicant_name} / 키워드: {analysis.keywords}"
    )

    return {
        "applicant_name": analysis.applicant_name,  # 이력서 검토 후 추출한 지원자 이름
        "resume_content": resume_text,
        "keywords": analysis.keywords,
        "question_count": 0,  # 질문 횟수 (아직 질문 전이므로 0)
        "is_finished": False,  # 질문 마무리 플래그 (아직 질문 전)
    }


# 2) 면접관 노드
async def interviewer_node(state: InterviewState):
    # TypedDict를 상속받은 state이므로 거대한 딕셔너리라고 보면 됨
    count = state.get("question_count", 0)  # 있으면 가져오고, 없으면 0 값

    # 질문은 최대 5개까지
    if count >= 5:
        print(" -> [면접관] 최대 질문 횟수에 도달하여 면접을 종료합니다.")
        return {"is_finished": True}

    print(f"\n[면접관] {count+1} 번째 질문을 고민 중입니다...")

    sys_msg = SystemMessage(
        content=f"""당신은 친절한 기술 면접관입니다.
    지원자: {state['applicant_name']} / 핵심 키워드: {state['keywords']}

    [진행 규칙]
    - 현재까지 당신이 던진 질문 횟수: {count}회
    - 질문이 3회 미만이면 검증이 부족하므로 '무조건' 꼬리질문이나 다른 질문을 던지세요. (is_finished=False)
    - 질문이 '3회 이상~4회 이하'라면, 답변이 충분한지 스스로 판단하여 조기종료(is_finished=True)하거나 질문을 5회까지 이어갈 수 있습니다.
    """
    )

    # 만약 대화 기록이 텅 비어있다면 (첫번째 질문 전)
    chat_history = state["messages"]
    if not chat_history:
        # Claude 모델은 대화 시작시 무조건 1개의 HumanMessage가 있어야 동작함
        # openai 모델은 systemprompt만 있어도 되는디
        chat_history = [
            HumanMessage(content="면접을 시작하고 첫 번째 질문을 던져주세요.")
        ]

    action: InterviewerAction = await llm.with_structured_output(
        InterviewerAction
    ).ainvoke([sys_msg] + chat_history)

    # 3회 미만인데 LLM이 마음대로 종료하려 하면 강제취소
    if action.is_finished and count < 3:
        action.is_finished = False

    # 조기 종료시
    if action.is_finished:
        print(" -> [면접관] 충분한 검증이 완료되어 면접을 조기 종료합니다.")
        return {"is_finished": True}
    # 질문 이어갈 시
    else:
        print(f" -> [질문]: {action.question}")
        return {
            "messages": [AIMessage(content=action.question)],
            "question_count": count + 1,
            "is_finished": False,
        }


# 3) 평가자 노드
async def evaluator_node(state: InterviewState):
    print("\n[평가자] 질의응답 전체 기록을 분석하여 최종 합/불을 판단합니다...")
    prompt = f"""당신은 냉철한 평가자 입니다. 다음 대화 기록을 보고 지원자의 역량을 평가하세요.
    반드시 PASS 또는 FAIL 중 하나만 선택하고, 사유를 작성하세요.
    """

    result: EvaluatorResult = await llm.with_structured_output(EvaluatorResult).ainvoke(
        state["messages"] + [HumanMessage(content=prompt)]
    )

    print(f" -> [AI 평가 결과]: {result.status} (사유: {result.reasoning})")

    return {"evaluator_result": result.status, "evaluator_reason": result.reasoning}


# 4) HR 마무리 노드 (이메일은 그냥 내용 출력만!)
async def hr_end_node(state: InterviewState):
    print("\n[HR 담당자] 인사권자의 최종 결정을 접수하여 이메일을 발송합니다.")
    send_final_email(state["applicant_name"], state["final_decision"])
    return {}


# ====================================================
# 4. 조건부 라우팅 함수
# ====================================================


def route_after_interview(state: InterviewState):
    # 질문 끝낸다고 판단하면 -> 평가자
    if state.get("is_finished", False) == True:
        return "evaluator"
    # 아니면 다시 자기 -> 면접관
    return "interviewer"


# 그래프 및 노드 구성
graph = StateGraph(InterviewState)
graph.add_node("hr_start", hr_start_node)
graph.add_node("interviewer", interviewer_node)
graph.add_node("evaluator", evaluator_node)
graph.add_node("hr_end", hr_end_node)

graph.add_edge(START, "hr_start")
graph.add_edge("hr_start", "interviewer")
graph.add_conditional_edges("interviewer", route_after_interview)
graph.add_edge("evaluator", "hr_end")
graph.add_edge("hr_end", END)

app = graph.compile(
    checkpointer=MemorySaver(),
    # interrupt_after: 특정 노드가 실행된 후 멈추도록 설정 (듀얼 HITL 적용)
    interrupt_after=["interviewer", "evaluator"],
)


# ====================================================
# 5. 메인 루프
# ====================================================
async def main():
    config = {"configurable": {"thread_id": "user1"}}
    initial_state = {"messages": []}

    print("=====================================")
    print("[HR 시스템] AI 면접 시스템 시작")
    print("=====================================\n")

    # 노드에 이미 출력문이 다 있기 때문에 app 객체가 스트리밍으로만 출력하도록 pass 설정
    async for _ in app.astream(initial_state, config, stream_mode="updates"):
        pass

    while True:
        # 상태 가져와서 다음 실행될 노드 확인
        snapshot = app.get_state(config)
        next_step = snapshot.next

        # 다음 실행될 노드가 없다면 (END 노드는 속이 비어있음)
        if not next_step:
            print("\n### 모든 채용 프로세스가 종료되었습니다.")
            break

        # 면접관 노드라면
        if next_step[0] == "interviewer":
            user_input = input("\n 지원자 답변 (포기 'q'): ")
            if user_input.lower() == "q":
                break

            # state의 messages에 지원자 답변을 업데이트
            app.update_state(config, {"messages": [HumanMessage(content=user_input)]})

        # 평가자 노드라면
        # (면접관 노드가 실행을 끝내면 is_finished가 True가 되어 평가자로 넘어간 상황)
        elif next_step[0] == "evaluator":
            print("\n 질문이 끝났습니다. 데이터를 평가자에게 넘깁니다...")

        # hr_end 라면
        elif next_step[0] == "hr_end":
            print("\n" + "=" * 50)
            print("### [인사팀장 결재 대기] ###")
            print(f"지원자: {snapshot.values['applicant_name']}")
            print(
                f"AI 평가: [{snapshot.values['evaluator_result']}] ({snapshot.values['evaluator_reason']})"
            )
            print("=" * 50)

            final_choice = input(" ▶ 최종 결정을 입력하세요 (PASS/FAIL):")
            app.update_state(config, {"final_decision": final_choice.upper()})

        # stream 형식 비동기 출력
        async for _ in app.astream(None, config, stream_mode="updates"):
            pass


if __name__ == "__main__":
    asyncio.run(main())
