
import os
from mcp.server.fastmcp import FastMCP

# 서버 이름 설정 (시스템 내부적으로 사용되는 명칭)
mcp = FastMCP("PythonFileServer")


# 경로 내 파일 목록보기 도구
 # @mcp.tool() : MCP에서 함수를 도구로 만드는 명령
 # "~" 기호는 'C:/User/사용자PC명' 경로(홈 경로)를 뜻함
@mcp.tool()
def list_my_file(path: str = "~") -> list :
    """지정된 경로의 파일 목록을 반환합니다.
    경로가 없으면 기본적으로 사용자 홈 폴더를 조회합니다.
    """

    # expanduser: 경로 관련 기호들을 절대 경로로 바꿔주는 함수
    real_path = os.path.expanduser(path)

    try :
        # listdir : 경로 내 파일명 반환
        return os.listdir(real_path)
    except FileNotFoundError:
        return [f"에러: {real_path} 경로를 찾을 수 없습니다."]

# 파일 내용 읽기 도구
@mcp.tool()
def read_my_file(filepath: str) -> str :
    """지정된 절대 경로의 파일 (txt, csv, py 등) 내용을 읽어옵니다."""

    real_path = os.path.expanduser(filepath)

    # 허용할 확장자 입력
    allowed_extensions = ('.txt', '.csv', '.json', '.py', '.pdf', '.ipynb')

    # endswith : 문자열이 특정 글자로 끝나는지 확인
    if not real_path.lower().endswith(allowed_extensions) :
        return """에러: 이 도구는 txt, csv, json, py, pdf, ipynb 파일만 읽을 수 있습니다."""

    try :
        # 용량 검사: 파일이 5MB 이상이면 읽기 거부 (토큰 초과 방지)
        if os.path.getsize(real_path) > (5 * 1024 * 1024) :
            return """에러: 파일 크기가 너무 큽니다.(5MB 초과) LLM 토큰 제한을 위해 읽기를 거부합니다."""

        with open(real_path, "r", encoding='utf-8') as f :
            return f.read()

    # 파일 경로를 찾을 수 없는 경우
    except FileNotFoundError :
        return f"""에러: '{real_path}' 경로를 찾을 수 없습니다. list_my_files 도구로 경로를 먼저 확인하세요."""

    # 텍스트로 읽어올 수 없는 경우
    except UnicodeDecodeError :
        return f"""에러: '{real_path}'의 파일을 텍스트 형식으로 읽을 수 없습니다. (인코딩 혹인 바이너리 파일 문제)"""


# 파이썬에서 특정 파일을 터미널에서 직접 실행하는 코드
# claude desktop이 위 도구들을 실행할 때 해당 코드를 사용함
if __name__ == "__main__" :
    mcp.run()
