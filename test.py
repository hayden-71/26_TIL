import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
API_KEY = os.getenv("MYREALTRIP_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# 날짜 설정 (오늘 기준 +7일 ~ +8일)
checkin = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
checkout = (datetime.now() + timedelta(days=8)).strftime("%Y-%m-%d")

pet_keywords = ["반려", "애견", "강아지", "펫", "pet", "Pet", "동물"]

# 반려동물 친화 숙소가 많은 도시들
cities = ["제주", "서울", "부산", "강원", "경기", "가평", "속초", "전주"]

all_stays = {}

for city in cities:
    payload = {
        "keyword": city,
        "checkIn": checkin,
        "checkOut": checkout,
        "adultCount": 2,
        "isDomestic": True,
        "perPage": 100,
    }
    response = requests.post(
        "https://partner-ext-api.myrealtrip.com/v1/products/accommodation/search",
        headers=headers,
        json=payload,
    )

    if response.status_code == 200:
        data = response.json()
        items = data.get("data", {}).get("items", [])

        # 상품명 or 설명에 반려동물 키워드 필터링
        filtered = [
            item
            for item in items
            if any(
                kw in item.get("itemName", "") + item.get("description", "")
                for kw in pet_keywords
            )
        ]

        print(f"🏨 '{city}': 전체 {len(items)}개 → 필터 후 {len(filtered)}개")

        for item in filtered:
            all_stays[item.get("gid")] = item
    else:
        print(f"❌ '{city}' 실패: {response.status_code} - {response.text}")

print(f"\n✅ 반려동물 친화 숙소 총 {len(all_stays)}개\n")
for i, item in enumerate(all_stays.values(), 1):
    print(f"{i}. {item.get('itemName')}")
    print(f"   💰 {item.get('priceDisplay')} | ⭐ {item.get('reviewScore')}")
    print()
