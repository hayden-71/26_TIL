import urllib.request, json, os
from dotenv import load_dotenv

# 내 환경변수 불러오기
load_dotenv()
token = os.getenv("SLACK_BOT_TOKEN")
channel = os.getenv("SLACK_CHANNEL_ID")

print("슬랙에 직접 전송 시도 중...")

url = "https://slack.com/api/chat.postMessage"
data = json.dumps({"channel": channel, "text": "왜요쌤 팩트체크 테스트!"}).encode(
    "utf-8"
)
req = urllib.request.Request(
    url,
    data=data,
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(req) as res:
        # 슬랙이 보내는 진짜 답변(에러 원인)을 화면에 출력!
        print("결과:", json.loads(res.read().decode()))
except Exception as e:
    print("에러 발생:", e)
