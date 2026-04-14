import os
import requests
from dotenv import load_dotenv
import streamlit as st

# 1. 환경 변수 불러오기 (.env 파일)
load_dotenv()
API_KEY = os.getenv("MYREALTRIP_API_KEY")

# 2. 웹페이지 기본 설정
st.set_page_config(page_title="도시별 카테고리 검색기", layout="centered")

st.title("🗺️ 도시별 투어/티켓 카테고리 검색기")
st.markdown(
    "마이리얼트립에 등록된 도시별 공식 카테고리 목록과 검색용 코드를 확인해 보세요!"
)

# 3. 사용자 입력창 만들기 (웹 화면용 input)
city_name = st.text_input(
    "검색할 도시 이름을 입력하세요 (예: 제주, 오사카, 파리, 서울)", value="제주"
)

# 4. 버튼을 눌렀을 때 실행될 로직
if st.button("카테고리 조회하기"):
    if not API_KEY:
        st.error("🚨 API 키를 찾을 수 없습니다. .env 파일을 확인해 주세요.")
    else:
        # 로딩 스피너 보여주기
        with st.spinner(f"'{city_name}'의 데이터를 마이리얼트립에서 가져오는 중..."):
            url = "https://partner-ext-api.myrealtrip.com/v1/products/tna/categories"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",  # POST 요청의 핵심!
            }
            payload = {"city": city_name}

            try:
                # POST 방식으로 데이터 요청
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    # 터미널에서 성공했던 그 '상자 두 번 열기' 로직!
                    categories = data.get("data", {}).get("categories", [])

                    if categories:
                        # print() 대신 st.success()로 웹 화면에 출력
                        st.success(
                            f"✅ '{city_name}'에서 총 {len(categories)}개의 카테고리를 찾았습니다!"
                        )

                        # 결과를 예쁜 박스(info) 형태로 나열
                        for cat in categories:
                            name = cat.get("name")
                            value = cat.get("value")
                            st.info(f"🏷️ **{name}** (검색용 코드: `{value}`)")
                    else:
                        st.warning(
                            f"⚠️ '{city_name}'에 해당하는 카테고리가 없거나 지원하지 않는 도시입니다."
                        )
                else:
                    st.error(f"🚨 API 호출 실패 (상태 코드: {response.status_code})")
                    st.code(response.text)

            except Exception as e:
                st.error(f"🚨 통신 중 알 수 없는 오류가 발생했습니다: {e}")
