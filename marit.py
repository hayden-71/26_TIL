import os
import streamlit as st
import requests
from dotenv import load_dotenv

# 환경설정에 맞게 라이브러리 임포트
try:
    from google import genai
except ImportError:
    import google.genai as genai

load_dotenv()

# 키 불러오기
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MARIT_API_KEY = os.getenv("MYREALTRIP_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

st.title("🐾 반려동물 HOT 여행 추천")
st.subheader("마이리얼트립 실시간 데이터를 AI가 분석합니다.")


# 1. API 설정
API_KEY = "qtocW6E4R9JEU979qpwwigbCzjm1UMKiTxVYIQYiMZ7uOcoClqWvHhwCvWvQOPtp"
BASE_URL = "https://partner-ext-api.myrealtrip.com"
ENDPOINT = "/v1/products/flight/calendar"

# 2. 요청 헤더 설정
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 3. 요청 바디(파라미터) 설정 - 명세서의 필수값 기반
payload = {
    "startDate": "2026-04-14",  # 조회 시작일
    "endDate": "2026-04-20",    # 조회 종료일
    "depCityCd": "ICN",         # 출발 도시 (인천)
    "arrCityCd": "BKK",         # 도착 도시 (방콕)
    "period": 5                 # 체류 기간 (5일)
}

# 4. POST 요청 실행
response = requests.post(
    f"{BASE_URL}{ENDPOINT}",
    headers=headers,
    json=payload
)

# 5. 결과 확인
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("성공 데이터:")
    print(response.json())
else:
    print(f"에러 발생: {response.text}")


def get_marit_data():
    # url = "https://partner-ext-api.myrealtrip.com/v1/products"
    # headers = {"Authorization": f"Bearer {MARIT_API_KEY}"}
    # params = {"keyword": "일본"}

    # response = requests.get(url, headers=headers, params=params)

    # if response.status_code == 200:
    #     st.success("✅ 500 에러 탈출 성공!")
    #     return response.json().get("data", [])
    # else:
    #     st.error(f"🚨 API 호출 실패 (상태 코드: {response.status_code})")
    #     # 서버가 왜 뻗었는지 남긴 마지막 메시지를 화면에 출력합니다.
    #     st.code(response.text)
    #     return []

    # API 승인이 날 때까지 사용할 임시 데이터 (가짜 데이터)
    st.info("💡 현재 API 권한 승인 대기 중으로 임시 데이터를 사용합니다.")

    mock_data = [
        {
            "productName": "[제주] 반려견과 함께하는 오름 투어 스냅촬영",
            "price": 45000,
            "category": "투어",
        },
        {
            "productName": "[강원] 댕댕이 맘껏 뛰어노는 펜션 1박",
            "price": 120000,
            "category": "숙박",
        },
        {
            "productName": "[서울 근교] 남양주 애견동반 프라이빗 바베큐장",
            "price": 50000,
            "category": "액티비티",
        },
    ]

    return mock_data  # 에러 없이 무조건 가짜 데이터를 뱉어냅니다.


if st.button("지금 인기 있는 테마 보기"):
    with st.spinner("AI가 실시간 상품을 분석 중입니다... 🐕🐈"):
        products = get_marit_data()

        if products:
            # AI에게 상품 리스트를 주고 분석 요청
            prompt = f"""
            다음은 마이리얼트립의 반려동물 여행 상품 리스트야: {products}
            이 중에서 가장 매력적인 테마 3가지를 뽑아서 예쁘게 추천해줘.
            각 테마별로 어울리는 이모지도 꼭 넣어줘.
            """

            response = client.models.generate_content(
                model="gemini-1.5-flash", contents=prompt
            )
            st.markdown(response.text)
        else:
            st.warning(
                "현재 검색된 반려동물 상품이 없거나 데이터를 불러오지 못했습니다."
            )
