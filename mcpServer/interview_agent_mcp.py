
import os
from dotenv import load_dotenv
import asyncio
from typing import Annotated, TypedDict, List, Literal
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_upstage import UpstageDocumentParseLoader
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool   # [도구 클래스 추가]

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

# [MCP 전용 클래스 추가]
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
# [슬랙 채널 ID 추가]
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

# [글로벌 변수: MCP 전용 세션을 담아둘 객체(main 함수에서 연결됨) 추가]
tavily_session: ClientSession = None
slack_session: ClientSession = None

# [LLM과 외부 MCP 서버를 연결해주는 도구(내부에서 Tavily 사용) 추가]
@tool
async def verify_facts_with_tavily(query: str) -> str:
    """지원자의 답변 중 사실 확인이 필요한 기술, 기업 정보, 뉴스 등을 인터넷으로 검색합니다."""
    # LLM은 URL이나 복잡한 명령어 없이 검색어(query)만 던지면 됨!
    try:
        # 실제 Tavily MCP 서버로 요청 전송
        result = await tavily_session.call_tool(
            # tavily 검색 도구 명칭
            "tavily_search",
            arguments={"query": query}
        )
        return result.content[0].text

    except Exception as e:
        return f"검색 중 오류가 발생했습니다: {e}"

class InterviewState(TypedDict) :
    messages: Annotated[list, add_messages]
    applicant_name: str         
    resume_content: str         
    keywords: List[str]         
    question_count: int         
    is_finished: bool           
    evaluator_result: str       
    evaluator_reason: str       
    final_decision: str         

class HRAnalysis(BaseModel) :
    applicant_name: str = Field(
        description="이력서에서 추출한 지원자 이름"
    )
    keywords: List[str] = Field(
        description="면접에 활용할 수 있는 핵심 기술/경험 키워드 3~5개"
    )

class InterviewerAction(BaseModel) :
    question: str = Field(
        default="", 
        description="지원자에게 던질 꼬리 질문 (종료 시 빈 문자열)"
    )
    is_finished: bool = Field(
        description="충분히 검증되어 질문을 그만하고 평가자에게 넘길거면 True, 아니면 False"
    )

class EvaluatorResult(BaseModel) :
    status: Literal["PASS", "FAIL"] = Field(
        description="최종 판정 (반드시 PASS 또는 FAIL)"
    )
    reasoning: str = Field(
        description="합격/불합격으로 판단한 결정적 사유 3문장 이내"
    )

llm = ChatAnthropic(
    model="claude-sonnet-4-6",
    temperature=0.2,
    api_key=ANTHROPIC_API_KEY
)


# [최종 합불 이메일 보내기 함수는 제거(슬랙 전송으로 대체)]


async def hr_start_node(state: InterviewState) :
    print("[HR 담당자] Upstage API로 이력서를 분석합니다...")
    file_path = "mcpServer/김민정_DBA_이력서.pdf"

    loader = UpstageDocumentParseLoader(
        file_path, 
        api_key=UPSTAGE_API_KEY, 
        split="element", 
        output_format="markdown"
    )
    resume_text = "\n".join([doc.page_content for doc in loader.load()])

    prompt = f"""다음 이력서를 분석하여 지원자 이름과 면접용 핵심 키워드를 추출하세요.
    [이력서]
    {resume_text}
    """
    analysis: HRAnalysis = await llm.with_structured_output(HRAnalysis).ainvoke([HumanMessage(content=prompt)])

    print(f" → [추출 완료] 지원자: {analysis.applicant_name} / 키워드: {analysis.keywords}")
    return {
        "applicant_name": analysis.applicant_name,
        "resume_content": resume_text,
        "keywords": analysis.keywords,
        "question_count": 0,
        "is_finished": False
    }

async def interviewer_node(state: InterviewState) :
    count = state.get("question_count", 0)
    if count >= 5 :
        print(" → [면접관] 최대 질문 횟수(5회)에 도달하여 면접을 종료합니다.")
        return {"is_finished": True}

    print(f"\n[면접관] {count+1}번째 질문을 고민 중입니다...")
    sys_msg = SystemMessage(content=f"""
    당신은 친절한 기술 면접관입니다.
    지원자: {state['applicant_name']} / 핵심 키워드: {state['keywords']}

    [진행 규칙]
    - 현재까지 당신이 던진 질문 횟수: {count}회
    - 질문이 3회 미만이면 검증이 부족하므로 '무조건' 꼬리질문이나 
    다른 질문을 던지세요 (is_finished=False).
    - 질문이 '3회 이상 ~ 4회 이하'라면, 답변이 충분한지 스스로 판단하여
    조기 종료(is_finished=True)하거나 질문을 5회까지 이어갈 수 있습니다.
    """)

    chat_history = state["messages"]
    if not chat_history :
        chat_history = [HumanMessage(content="면접을 시작하고 첫 번째 질문을 던져주세요.")]

    action: InterviewerAction = await llm.with_structured_output(InterviewerAction).ainvoke([sys_msg] + chat_history)

    if action.is_finished and count < 3 :
        action.is_finished = False

    if action.is_finished :
        print(" → [면접관] 충분한 검증이 완료되어 면접을 조기 종료합니다.")
        return {"is_finished": True}
    else :
        print(f" → [질문]: {action.question}")
        return {
            "messages": [AIMessage(content=action.question)],
            "question_count": count + 1,
            "is_finished": False
        }


# [검색 도구를 활용하는 평가자 노드]
async def evaluator_node(state: InterviewState) :
    print("\n[평가자] 전체 기록을 분석하며 사실 관계를 팩트체크(Tavily사용) 합니다...")
    prompt = f"""당신은 냉철한 평가자입니다. 대화 기록 중 지원자가 주장한 
    기술적 사실이나 기업 정보가 의심스럽다면 반드시 'verify_facts_with_tavily'
    도구를 써서 인터넷을 검색하세요.
    검색을 마쳤거나 검색이 필요 없다면, 최종적으로 지원자의 역량을 평가하세요."""

    messages = state["messages"] + [HumanMessage(content=prompt)]

    # LLM에 Tavily 검색 도구 쥐여주기
    check_llm = llm.bind_tools([verify_facts_with_tavily])
    response = await check_llm.ainvoke(messages)

    # LLM이 도구를 호출했다면
    if response.tool_calls :
        print("[팩트체크 가동] 의심스러운 내용을 인터넷으로 검색합니다...")
        messages.append(response)  # LLM의 도구 사용 정보를 메시지 저장

        for tool in response.tool_calls :
            if tool["name"] == "verify_facts_with_tavily" :
                # 파이썬에서 직접 도구 실행 후 결과 가져오기
                tool_msg = await verify_facts_with_tavily.ainvoke(tool)
                messages.append(tool_msg)   # 검색 결과 메시지 저장
                print(f" -> [검색 완료] 관련 정보를 확보했습니다.")

    print("[최종 판정] 검증된 데이터를 바탕으로 평가서를 작성합니다.")
    result: EvaluatorResult = await llm.with_structured_output(EvaluatorResult).ainvoke(messages)

    print(f" → [AI 평가 결과]: {result.status} (사유: {result.reasoning})")
    return {"evaluator_result": result.status, "evaluator_reason": result.reasoning}


# [이메일 출력문 대신 슬랙 전송 마무리 노드]
async def hr_end_node(state: InterviewState) :
    applicant = state["applicant_name"]
    decision = state["final_decision"]
    reason = state["evaluator_reason"]

    print("\n[HR 담당자] 인사권자의 최종 결정을 접수하여 Slack으로 발송합니다.")

    if decision == "PASS":
        slack_text = f"*[최종 합격]* {applicant} 지원자님 축하합니다!\n - AI 평가 사유: {reason}"
    else:
        slack_text = f"*[불합격]* {applicant} 지원자님 수고하셨습니다.\n - AI 평가 사유: {reason}"

    try:
        # 슬랙 MCP 서버 호출 (도구 이름은 mcp-server-slack 서버 기준)
        await slack_session.call_tool(
            "slack_post_message",   # 도구명
            arguments={
                "channel_id": SLACK_CHANNEL_ID,
                "text": slack_text
            }
        )
        print(" → [Slack 발송 성공!] 채널을 확인하세요.")

    except Exception as e:
        print(f" → [Slack 발송 실패]: {e}")

    return {}


def route_after_interviewer(state: InterviewState) :
    if state.get("is_finished", False) == True : 
        return "evaluator"
    return "interviewer"

graph = StateGraph(InterviewState)
graph.add_node("hr_start", hr_start_node)
graph.add_node("interviewer", interviewer_node)
graph.add_node("evaluator", evaluator_node)
graph.add_node("hr_end", hr_end_node)

graph.add_edge(START, "hr_start")
graph.add_edge("hr_start", "interviewer")
graph.add_conditional_edges("interviewer", route_after_interviewer)
graph.add_edge("evaluator", "hr_end")
graph.add_edge("hr_end", END)

app = graph.compile(
    checkpointer=MemorySaver(), 
    interrupt_after=["interviewer", "evaluator"]
)

# [메인 루프 (MCP 연동)]
async def main() :
    # global: 전역변수(함수 밖에서도 사용가능한 변수) 설정
    global tavily_session, slack_session

    # 아래 환경변수들은 파이썬이 직접 실행하는것이 아니라 npx(node.js서버)가 실행하게
    # 되는데, 이때 우리의 환경변수를 copy해서 npx실행시 활용하게 함
    safe_env = os.environ.copy()   
    safe_env["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
    safe_env["SLACK_BOT_TOKEN"] = os.getenv("SLACK_BOT_TOKEN")
    # <api.slack.com/apps 에서 OAuth & Permissions 탭에 들어간 뒤 맨 상단 url에
    #  T로 시작되는 문자열이 SLACK_TEAM_ID 이며 이를 .env파일에 환경변수로 등록해야함>
    safe_env["SLACK_TEAM_ID"] = os.getenv("SLACK_TEAM_ID")

    # Tavily 서버
    tavily_params = StdioServerParameters(
        # npx는 npx.cmd로 사용, uvx는 uvx.exe로 사용(mac은 npx, uvx로 사용)
        command="npx.cmd",
        args=["-y","tavily-mcp"],  
        env=safe_env   # 환경 변수 전달
    )

    # Slack 서버
    slack_params = StdioServerParameters(
        command="npx.cmd",
        # 엔트로픽 공식 슬랙 MCP 서버
        args=["-y","@modelcontextprotocol/server-slack"],
        env=safe_env
    )

    # <args 작성 방식> - 해당 서버를 만든 개발자의 github이나 공식문서를 볼 것!
     # 1.엔트로픽 공식 방식(npx @modelcontextprotocol/... 라고 적혀있을 때)
     #  -> args=["@modelcontextprotocol/서버명"]
     # 2.API 제공 업체가 직접 PyPI이나 npm에 등록한 방식
     #  (npm링크: https://www.npmjs.com/)
     #  (PyPI링크: https://pypi.org/) 
     #  -> args=["서버명"]
     # 3.스미더리 외부 플랫폼 방식
     #  -> args=["-y", "@smithery/cli@latest", "run", "서버명"]

    print("MCP 서버(Tavily, Slack) 부팅 및 파이프라인 연결 중...")

    # 2개의 서버를 동시에 백그라운드에 띄우기
    async with (
        stdio_client(tavily_params) as (tr, tw),
        ClientSession(tr, tw) as ts,
        stdio_client(slack_params) as (sr, sw),
        ClientSession(sr, sw) as ss
    ):

        await ts.initialize()
        await ss.initialize()

        # 각 전역 변수에 세션 객체 업데이트
        # (추후 에이전트가 도구를 사용할 때 활성화된 세션을 사용)
        tavily_session = ts
        slack_session = ss
        print("시스템 온라인! (웹 검색 & 슬랙 연동 완료)\n")

        config = {"configurable": {"thread_id": "user_1"}}
        initial_state = {"messages": []}

        print("="*40)
        print("[HR 시스템] AI 면접 시스템 가동")
        print("="*40)

        # 첫 실행
        async for _ in app.astream(initial_state, config, stream_mode="updates"): pass

        while True :
            snapshot = app.get_state(config)
            next_step = snapshot.next

            if not next_step :
                print("\n### 모든 채용 프로세스가 종료되었습니다. 서버 연결을 닫습니다. ###")
                break

            if next_step[0] == "interviewer" :
                user_input = input("\n지원자 답변 (포기 'q'): ")
                if user_input.lower() == 'q' : break
                app.update_state(config, {"messages": [HumanMessage(content=user_input)]})

            elif next_step[0] == "evaluator" :
                print("\n질문이 끝났습니다. 데이터를 평가자에게 넘깁니다...")

            elif next_step[0] == "hr_end" :
                print("\n" + "="*50)
                print("### [인사팀장 결재 대기] ###")
                print(f"지원자: {snapshot.values['applicant_name']}")
                print(f"AI 평가: [{snapshot.values['evaluator_result']}] ({snapshot.values['evaluator_reason']})")
                print("="*50)

                final_choice = input(" ▶ 최종 결정을 입력하세요 (PASS / FAIL): ")
                app.update_state(config, {"final_decision": final_choice.upper()})

            async for _ in app.astream(None, config, stream_mode="updates"): pass

if __name__ == "__main__" :
    asyncio.run(main())
