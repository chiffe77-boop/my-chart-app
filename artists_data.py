"""
K-POP Comeback Radar — 확장 아티스트 데이터베이스 (v2 초안)

설계 원칙
---------
1. 그룹(group)과 솔로(solo)를 완전히 분리된 엔티티로 취급한다.
   - 솔로 엔티티는 `group_id`로 원 소속 그룹을 참조한다 (없으면 완전 개인 솔로).
   - 사이드바에서는 "그룹으로 보기 / 멤버 솔로로 보기"를 별도 선택지로 노출한다.
2. 여기 포함된 솔로 멤버는 "공식 솔로 음반(정규/미니/싱글)을 낸 적이 있는 멤버"만 포함한다.
   유닛 활동(예: SEVENTEEN BSS, NCT U 등)은 이번 버전 범위에서 제외 — 필요하면 다음 단계에서 추가.
3. generation은 데뷔 연도 기준 대략적 구분(3세대: 2013-2019 / 4세대: 2020-2023)이며
   엄밀한 업계 정의와 다를 수 있음을 UI에 각주로 명시할 것.

TODO(다음 단계)
---------------
- [ ] 실제 애플뮤직 아티스트 ID(iTunes artistId) 매핑 — 이름 검색만으로는 동명이인/오타 그룹 오탐 가능
- [ ] 유닛 활동(2인조 이상 서브그룹) 지원 여부 논의
- [ ] 서클차트 공개 보도자료 기반 초동 판매량 시드 데이터(seed_sales.py)와 연결
"""

from __future__ import annotations

from typing import Literal, TypedDict


class ArtistEntry(TypedDict, total=False):
    display_name: str
    kind: Literal["group", "solo"]
    group_id: str | None          # solo 인 경우 소속 그룹 id, 없으면 None
    members: list[str]            # group 인 경우만
    generation: Literal[3, 4]
    debut_year: int
    apple_query: str
    youtube_query: str
    global_news_query: str
    naver_news_query: str
    emoji: str


ARTISTS: dict[str, ArtistEntry] = {

    # ---------------------------------------------------------------
    # 3세대 그룹
    # ---------------------------------------------------------------
    "bts": {
        "display_name": "BTS", "kind": "group", "group_id": None,
        "members": ["RM", "Jin", "SUGA", "j-hope", "Jimin", "V", "Jung Kook"],
        "generation": 3, "debut_year": 2013,
        "apple_query": "BTS", "youtube_query": "BTS official BANGTANTV",
        "global_news_query": "BTS K-pop", "naver_news_query": "방탄소년단", "emoji": "💜",
    },
    "blackpink": {
        "display_name": "BLACKPINK", "kind": "group", "group_id": None,
        "members": ["Jisoo", "Jennie", "Rosé", "Lisa"],
        "generation": 3, "debut_year": 2016,
        "apple_query": "BLACKPINK", "youtube_query": "BLACKPINK official",
        "global_news_query": "BLACKPINK", "naver_news_query": "블랙핑크", "emoji": "🖤",
    },
    "twice": {
        "display_name": "TWICE", "kind": "group", "group_id": None,
        "members": ["Nayeon", "Jeongyeon", "Momo", "Sana", "Jihyo", "Mina", "Dahyun", "Chaeyoung", "Tzuyu"],
        "generation": 3, "debut_year": 2015,
        "apple_query": "TWICE", "youtube_query": "TWICE official",
        "global_news_query": "TWICE K-pop", "naver_news_query": "트와이스", "emoji": "🍭",
    },
    "red_velvet": {
        "display_name": "Red Velvet", "kind": "group", "group_id": None,
        "members": ["Irene", "Seulgi", "Wendy", "Joy", "Yeri"],
        "generation": 3, "debut_year": 2014,
        "apple_query": "Red Velvet", "youtube_query": "Red Velvet official SMTOWN",
        "global_news_query": "Red Velvet K-pop", "naver_news_query": "레드벨벳", "emoji": "🍒",
    },
    "seventeen": {
        "display_name": "SEVENTEEN", "kind": "group", "group_id": None,
        "members": ["S.Coups", "Jeonghan", "Joshua", "Jun", "Hoshi", "Wonwoo", "Woozi",
                    "DK", "Mingyu", "The8", "Seungkwan", "Vernon", "Dino"],
        "generation": 3, "debut_year": 2015,
        "apple_query": "SEVENTEEN", "youtube_query": "SEVENTEEN official",
        "global_news_query": "SEVENTEEN K-pop", "naver_news_query": "세븐틴", "emoji": "💎",
    },
    "stray_kids": {
        "display_name": "Stray Kids", "kind": "group", "group_id": None,
        "members": ["Bang Chan", "Lee Know", "Changbin", "Hyunjin", "Han", "Felix", "Seungmin", "I.N"],
        "generation": 3, "debut_year": 2018,
        "apple_query": "Stray Kids", "youtube_query": "Stray Kids official",
        "global_news_query": "Stray Kids", "naver_news_query": "스트레이 키즈", "emoji": "⚡",
    },
    "gidle": {
        "display_name": "(G)I-DLE", "kind": "group", "group_id": None,
        "members": ["Miyeon", "Minnie", "Soyeon", "Yuqi", "Shuhua"],
        "generation": 3, "debut_year": 2018,
        "apple_query": "(G)I-DLE", "youtube_query": "(G)I-DLE official",
        "global_news_query": "(G)I-DLE K-pop", "naver_news_query": "여자아이들", "emoji": "🐰",
    },
    "nct_dream": {
        "display_name": "NCT DREAM", "kind": "group", "group_id": None,
        "members": ["Mark", "Renjun", "Jeno", "Haechan", "Jaemin", "Chenle", "Jisung"],
        "generation": 3, "debut_year": 2016,
        "apple_query": "NCT DREAM", "youtube_query": "NCT DREAM official",
        "global_news_query": "NCT DREAM", "naver_news_query": "엔시티 드림", "emoji": "💚",
    },
    "nct_127": {
        "display_name": "NCT 127", "kind": "group", "group_id": None,
        "members": ["Taeyong", "Jaehyun", "Doyoung", "Yuta", "Jungwoo", "Mark", "Haechan"],
        "generation": 3, "debut_year": 2016,
        "apple_query": "NCT 127", "youtube_query": "NCT 127 official",
        "global_news_query": "NCT 127", "naver_news_query": "엔시티 127", "emoji": "🖤",
    },
    "ateez": {
        "display_name": "ATEEZ", "kind": "group", "group_id": None,
        "members": ["Hongjoong", "Seonghwa", "Yunho", "Yeosang", "San", "Mingi", "Wooyoung", "Jongho"],
        "generation": 3, "debut_year": 2018,
        "apple_query": "ATEEZ", "youtube_query": "ATEEZ official",
        "global_news_query": "ATEEZ K-pop", "naver_news_query": "에이티즈", "emoji": "🏴",
    },

    # ---------------------------------------------------------------
    # 4세대 그룹
    # ---------------------------------------------------------------
    "aespa": {
        "display_name": "aespa", "kind": "group", "group_id": None,
        "members": ["Karina", "Giselle", "Winter", "Ningning"],
        "generation": 4, "debut_year": 2020,
        "apple_query": "aespa", "youtube_query": "aespa official",
        "global_news_query": "aespa", "naver_news_query": "에스파", "emoji": "🪩",
    },
    "ive": {
        "display_name": "IVE", "kind": "group", "group_id": None,
        "members": ["Yujin", "Gaeul", "Rei", "Wonyoung", "Liz", "Leeseo"],
        "generation": 4, "debut_year": 2021,
        "apple_query": "IVE", "youtube_query": "IVE official",
        "global_news_query": "IVE K-pop", "naver_news_query": "아이브", "emoji": "✨",
    },
    "le_sserafim": {
        "display_name": "LE SSERAFIM", "kind": "group", "group_id": None,
        "members": ["Sakura", "Chaewon", "Yunjin", "Kazuha", "Eunchae"],
        "generation": 4, "debut_year": 2022,
        "apple_query": "LE SSERAFIM", "youtube_query": "LE SSERAFIM official",
        "global_news_query": "LE SSERAFIM", "naver_news_query": "르세라핌", "emoji": "🔥",
    },
    "newjeans": {
        "display_name": "NewJeans", "kind": "group", "group_id": None,
        "members": ["Minji", "Hanni", "Danielle", "Haerin", "Hyein"],
        "generation": 4, "debut_year": 2022,
        "apple_query": "NewJeans", "youtube_query": "NewJeans official",
        "global_news_query": "NewJeans", "naver_news_query": "뉴진스", "emoji": "🐰",
    },
    "itzy": {
        "display_name": "ITZY", "kind": "group", "group_id": None,
        "members": ["Yeji", "Lia", "Ryujin", "Chaeryeong", "Yuna"],
        "generation": 4, "debut_year": 2019,
        "apple_query": "ITZY", "youtube_query": "ITZY official",
        "global_news_query": "ITZY K-pop", "naver_news_query": "있지", "emoji": "🧡",
    },
    "txt": {
        "display_name": "TOMORROW X TOGETHER", "kind": "group", "group_id": None,
        "members": ["Soobin", "Yeonjun", "Beomgyu", "Taehyun", "Huening Kai"],
        "generation": 4, "debut_year": 2019,
        "apple_query": "TOMORROW X TOGETHER", "youtube_query": "TOMORROW X TOGETHER official",
        "global_news_query": "TXT K-pop", "naver_news_query": "투모로우바이투게더", "emoji": "🌙",
    },
    "enhypen": {
        "display_name": "ENHYPEN", "kind": "group", "group_id": None,
        "members": ["Jungwon", "Heeseung", "Jay", "Jake", "Sunghoon", "Sunoo", "Ni-ki"],
        "generation": 4, "debut_year": 2020,
        "apple_query": "ENHYPEN", "youtube_query": "ENHYPEN official",
        "global_news_query": "ENHYPEN", "naver_news_query": "엔하이픈", "emoji": "🌆",
    },
    "riize": {
        "display_name": "RIIZE", "kind": "group", "group_id": None,
        "members": ["Shotaro", "Eunseok", "Sungchan", "Seunghan", "Wonbin", "Sohee", "Anton"],
        "generation": 4, "debut_year": 2023,
        "apple_query": "RIIZE", "youtube_query": "RIIZE official",
        "global_news_query": "RIIZE K-pop", "naver_news_query": "라이즈", "emoji": "🌅",
    },
    "zb1": {
        "display_name": "ZEROBASEONE", "kind": "group", "group_id": None,
        "members": ["Sung Hanbin", "Kim Jiwoong", "Zhang Hao", "Seok Matthew",
                    "Kim Taerae", "Ricky", "Kim Gyuvin", "Han Yujin", "Park Gunwook"],
        "generation": 4, "debut_year": 2023,
        "apple_query": "ZEROBASEONE", "youtube_query": "ZEROBASEONE official",
        "global_news_query": "ZEROBASEONE K-pop", "naver_news_query": "제로베이스원", "emoji": "🌱",
    },
    "boynextdoor": {
        "display_name": "BOYNEXTDOOR", "kind": "group", "group_id": None,
        "members": ["Sungho", "Riwoo", "Taesan", "Leehan", "Jaehyun", "Woonhak"],
        "generation": 4, "debut_year": 2023,
        "apple_query": "BOYNEXTDOOR", "youtube_query": "BOYNEXTDOOR official",
        "global_news_query": "BOYNEXTDOOR K-pop", "naver_news_query": "보이넥스트도어", "emoji": "🏠",
    },
    "kep1er": {
        "display_name": "Kep1er", "kind": "group", "group_id": None,
        "members": ["Choi Yujin", "Mashiro", "Kim Chaehyun", "Huening Bahiyyih",
                    "Kim Dayeon", "Seo Youngeun", "Shen Xiaoting", "Kang Yeseo"],
        "generation": 4, "debut_year": 2022,
        "apple_query": "Kep1er", "youtube_query": "Kep1er official",
        "global_news_query": "Kep1er K-pop", "naver_news_query": "케플러", "emoji": "🚀",
    },
    "nmixx": {
        "display_name": "NMIXX", "kind": "group", "group_id": None,
        "members": ["Lily", "Haewon", "Sullyoon", "Bae", "Jinni", "Kyujin"],
        "generation": 4, "debut_year": 2022,
        "apple_query": "NMIXX", "youtube_query": "NMIXX official",
        "global_news_query": "NMIXX K-pop", "naver_news_query": "엔믹스", "emoji": "🎨",
    },
    "staych": {
        "display_name": "STAYC", "kind": "group", "group_id": None,
        "members": ["Sumin", "Sieun", "Isa", "Seeun", "Yoon", "J"],
        "generation": 4, "debut_year": 2020,
        "apple_query": "STAYC", "youtube_query": "STAYC official",
        "global_news_query": "STAYC K-pop", "naver_news_query": "스테이씨", "emoji": "🌟",
    },

    # ---------------------------------------------------------------
    # 솔로 (group_id로 원 소속 그룹 참조)
    # ---------------------------------------------------------------
    "rm": {
        "display_name": "RM", "kind": "solo", "group_id": "bts", "generation": 3, "debut_year": 2022,
        "apple_query": "RM", "youtube_query": "RM official BANGTANTV",
        "global_news_query": "RM BTS solo", "naver_news_query": "RM 솔로", "emoji": "📚",
    },
    "jin": {
        "display_name": "Jin", "kind": "solo", "group_id": "bts", "generation": 3, "debut_year": 2022,
        "apple_query": "Jin", "youtube_query": "Jin official BANGTANTV",
        "global_news_query": "Jin BTS solo", "naver_news_query": "진 솔로", "emoji": "🌹",
    },
    "agust_d": {
        "display_name": "Agust D (SUGA)", "kind": "solo", "group_id": "bts", "generation": 3, "debut_year": 2016,
        "apple_query": "Agust D", "youtube_query": "Agust D official",
        "global_news_query": "Agust D Suga solo", "naver_news_query": "슈가 솔로", "emoji": "🎤",
    },
    "jhope": {
        "display_name": "j-hope", "kind": "solo", "group_id": "bts", "generation": 3, "debut_year": 2018,
        "apple_query": "j-hope", "youtube_query": "j-hope official BANGTANTV",
        "global_news_query": "j-hope BTS solo", "naver_news_query": "제이홉 솔로", "emoji": "☀️",
    },
    "jimin": {
        "display_name": "Jimin", "kind": "solo", "group_id": "bts", "generation": 3, "debut_year": 2023,
        "apple_query": "Jimin", "youtube_query": "Jimin official BANGTANTV",
        "global_news_query": "Jimin BTS solo", "naver_news_query": "지민 솔로", "emoji": "🩰",
    },
    "v": {
        "display_name": "V", "kind": "solo", "group_id": "bts", "generation": 3, "debut_year": 2023,
        "apple_query": "V", "youtube_query": "V official BANGTANTV",
        "global_news_query": "V BTS solo", "naver_news_query": "뷔 솔로", "emoji": "🖤",
    },
    "jungkook": {
        "display_name": "Jung Kook", "kind": "solo", "group_id": "bts", "generation": 3, "debut_year": 2023,
        "apple_query": "Jung Kook", "youtube_query": "Jung Kook official BANGTANTV",
        "global_news_query": "Jung Kook BTS solo", "naver_news_query": "정국 솔로", "emoji": "🐰",
    },
    "jennie": {
        "display_name": "Jennie", "kind": "solo", "group_id": "blackpink", "generation": 3, "debut_year": 2018,
        "apple_query": "Jennie", "youtube_query": "Jennie official",
        "global_news_query": "Jennie BLACKPINK solo", "naver_news_query": "제니 솔로", "emoji": "🖤",
    },
    "jisoo": {
        "display_name": "Jisoo", "kind": "solo", "group_id": "blackpink", "generation": 3, "debut_year": 2023,
        "apple_query": "JISOO", "youtube_query": "JISOO official",
        "global_news_query": "Jisoo BLACKPINK solo", "naver_news_query": "지수 솔로", "emoji": "🌸",
    },
    "rose": {
        "display_name": "Rosé", "kind": "solo", "group_id": "blackpink", "generation": 3, "debut_year": 2021,
        "apple_query": "Rosé", "youtube_query": "Rosé official",
        "global_news_query": "Rosé BLACKPINK solo", "naver_news_query": "로제 솔로", "emoji": "🌹",
    },
    "lisa": {
        "display_name": "LISA", "kind": "solo", "group_id": "blackpink", "generation": 3, "debut_year": 2021,
        "apple_query": "LISA", "youtube_query": "LISA official",
        "global_news_query": "Lisa BLACKPINK solo", "naver_news_query": "리사 솔로", "emoji": "💃",
    },
    "nayeon": {
        "display_name": "Nayeon", "kind": "solo", "group_id": "twice", "generation": 3, "debut_year": 2022,
        "apple_query": "Nayeon", "youtube_query": "Nayeon official TWICE",
        "global_news_query": "Nayeon TWICE solo", "naver_news_query": "나연 솔로", "emoji": "🐥",
    },
    "jihyo": {
        "display_name": "Jihyo", "kind": "solo", "group_id": "twice", "generation": 3, "debut_year": 2023,
        "apple_query": "Jihyo", "youtube_query": "Jihyo official TWICE",
        "global_news_query": "Jihyo TWICE solo", "naver_news_query": "지효 솔로", "emoji": "🎀",
    },
    "wendy": {
        "display_name": "Wendy", "kind": "solo", "group_id": "red_velvet", "generation": 3, "debut_year": 2021,
        "apple_query": "Wendy", "youtube_query": "Wendy official SMTOWN",
        "global_news_query": "Wendy Red Velvet solo", "naver_news_query": "웬디 솔로", "emoji": "🍫",
    },
    "seulgi": {
        "display_name": "Seulgi", "kind": "solo", "group_id": "red_velvet", "generation": 3, "debut_year": 2022,
        "apple_query": "Seulgi", "youtube_query": "Seulgi official SMTOWN",
        "global_news_query": "Seulgi Red Velvet solo", "naver_news_query": "슬기 솔로", "emoji": "🦢",
    },
    "soyeon": {
        "display_name": "Soyeon", "kind": "solo", "group_id": "gidle", "generation": 3, "debut_year": 2020,
        "apple_query": "Soyeon", "youtube_query": "Soyeon official (G)I-DLE",
        "global_news_query": "Soyeon (G)I-DLE solo", "naver_news_query": "소연 솔로", "emoji": "🎧",
    },
    "karina_winter": {
        "display_name": "Karina & Winter (Girls on Top)", "kind": "solo", "group_id": "aespa",
        "generation": 4, "debut_year": 2024,
        "apple_query": "Girls on Top", "youtube_query": "Girls on Top aespa",
        "global_news_query": "Karina Winter aespa unit", "naver_news_query": "카리나 윈터 유닛", "emoji": "🎬",
    },
    "chaewon_sakura": {
        "display_name": "CHAEWON & SAKURA (LE SSERAFIM unit)", "kind": "solo", "group_id": "le_sserafim",
        "generation": 4, "debut_year": 2025,
        "apple_query": "Chaewon Sakura", "youtube_query": "Chaewon Sakura LE SSERAFIM",
        "global_news_query": "Chaewon Sakura unit", "naver_news_query": "채원 사쿠라 유닛", "emoji": "🌷",
    },
}


def get_display_options() -> list[tuple[str, str]]:
    """사이드바 selectbox에 넣을 (key, 표시용 라벨) 목록. 그룹 먼저, 솔로는 소속 그룹 옆에 들여쓰기."""
    options: list[tuple[str, str]] = []
    groups = {k: v for k, v in ARTISTS.items() if v["kind"] == "group"}
    solos_by_group: dict[str, list[str]] = {}
    for k, v in ARTISTS.items():
        if v["kind"] == "solo":
            solos_by_group.setdefault(v.get("group_id") or "", []).append(k)

    for gk, gv in sorted(groups.items(), key=lambda x: (-x[1]["generation"], x[1]["display_name"])):
        options.append((gk, f'{gv["emoji"]} {gv["display_name"]}'))
        for sk in solos_by_group.get(gk, []):
            sv = ARTISTS[sk]
            options.append((sk, f'   ↳ {sv["emoji"]} {sv["display_name"]} (솔로)'))
    return options


if __name__ == "__main__":
    groups = sum(1 for v in ARTISTS.values() if v["kind"] == "group")
    solos = sum(1 for v in ARTISTS.values() if v["kind"] == "solo")
    print(f"그룹 {groups}개, 솔로 {solos}개, 총 {len(ARTISTS)}개 엔티티")
    for k, label in get_display_options():
        print(f"  {k:20s} -> {label}")
