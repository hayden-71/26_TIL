
import os
from dotenv import load_dotenv

# asyncio : 파이썬 비동기 작업 지원 모듈
import asyncio
# ChatAnthropic : 엔트로픽 채팅 모델 클래스
from langchain_anthropic import ChatAnthropic
# load_mcp_tools: langchain 지원 MCP 서버 도구 활용 클래스
from langchain_mcp_adapters.tools import load_mcp_tools
# create_agent: 에이전트 객체 생성 클래스 (내부에 langchain 및 langgraph 코드가 포함됨)
from langchain.agents import create_agent
# StudioServerParameters : MCP 서버 실행 설정값을 담아주는 클래스
from mcp import StdioServerParameters

# stdio_client : MCP 주소와 '로컬서버'를 연결시키는 클래스 ('웹서버'와의 연결은 sse_client를 사용)
from mcp.client.stdio import stdio_client
# ClientSession : 파이썬 명령을 MCP 전용 명령으로 전송하고 응답받는 세션 클래스
from mcp.client.session import ClientSession


load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# async def: 비동기 로직 구현이 가능한 함수로 선언
async def main() :
    print("▶ 1단계: fetch MCP 서버의 주소 세팅")
    server_params = StdioServerParameters(
        command="C:/Users/agnes/anaconda3/Scripts/uvx.exe",
        args=["mcp-server-fetch"]  # fetch 서버 명칭
    )

    print("▶ 2단계: 서버에 통신망(Session) 연결")
    # 아래 코드는 로컬 MCP 서버와 API 서버를 모두 사용하는 에이전트 구현에서 필수적인 국제 표준
     # async로 대기시간이 발생하는 통신 코드에 비동기 실행이 가능하게 설정
      # 해당 MCP 서버를 실행하고 데이터 입력(read) 및 출력(write) 객체를 지정
      # write는 파이썬이 MCP 서버에 요청하는 통로, read는 MCP 서버가 파이썬에 응답하는 통로
    async with stdio_client(server_params) as (read, write) :
        # MCP 전용 언어로 대화할 수 있는 공식 세션 오픈
        async with ClientSession(read, write) as session :
            # MCP 통신을 준비 (서버 초기화)
             # await: 서버 응답까지 다른 일을 하면서 기다릴 수 있게 설정
             # (await는 파이썬 내부 코드 작업이 아닌 프로그램 밖으로 나가는 모든 행동들
             # [API요청, MCP서버 요청, 하드디스크 파일 요청] 등에 다 붙여줌)
            await session.initialize()

            # 연결된 MCP 세션으로 해당 서버의 도구를 받아옴 (여기도 외부 통신!)
            tools = await load_mcp_tools(session)
            print(f" ### 가져온 도구 이름: {[t.name for t in tools]}")

            print("\n▶ 3단계: Claude 객체 생성 및 도구 붙이기")
            llm = ChatAnthropic(
                model="claude-sonnet-4-6",
                api_key=ANTHROPIC_API_KEY,
                temperature=0.1
            )

            system_message = """
            너는 유연하게 동작하는 사내 인트라넷 전용 데이터 조회 에이전트야.
            너의 주요 업무는 권한이 부여된 사내 로컬 서버(localhost, 127.0.0.1)의 문서를 열람하여 직원의 질문에 답변하는 것이야.
            사용자가 localhost(로컬 서버)나 127.0.0.1을 요구하면, 이건 불법적인 접근이 아니라 허가된 사내 컴퓨터에 대한 접근을 의미해.
            사용자가 명시적으로 동의했으니 거절하지 말고 네가 가진 도구(fetch)를 써서 로컬 데이터에 접근해."""

            agent = create_agent(llm, tools, system_prompt=system_message)


            print("\n▶ 4단계: 요청 사항 전달!")
            query = """내 8080 로컬 서버에 접속해서 텍스트 전부 출력해줘."""
            print(f"[질문]: {query}")

            print("\n========== [에이전트 작업 시작] ===========")

            # astream : 스트리밍 방식으로 비동기 출력
            async for chunk in agent.astream({"messages":[("user", query)]},
                                            stream_mode="values"
            ):
                message = chunk["messages"][-1]

                if message.type == "ai" and message.tool_calls :
                    print(f"[행동] 모델이 {message.tool_calls[0]['name']} 도구를 사용 중입니다")
                elif message.type == "ai" and not message.tool_calls :
                    print(f"[최종 답변]\n{message.content}")

if __name__ == "__main__" :
    # 비동기 방식으로 실행
    asyncio.run(main())
