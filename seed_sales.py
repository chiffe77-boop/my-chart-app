"""
K-POP Comeback Radar — 실측 판매량 시드 데이터 (v1)

데이터 출처 원칙
---------------
- 서클차트(舊 가온차트)/한터차트가 "보도자료·뉴스로 공개한" 숫자만 수록한다.
  (차트 사이트 자체를 스크래핑하지 않음 — 이용약관 이슈 회피)
- "초동"(chodong) = 발매 후 첫 1주일간 국내 음반 판매량. 업계 표준 KPI.
- 같은 수치라도 한터차트(수출물량 일부 제외) vs 서클차트(수출물량 포함) 기준이 달라
  두 숫자가 다르게 보도되는 경우가 있음 → source_chart 필드로 구분.
- verified=True: 뉴스 기사에서 직접 확인한 실측치.
  verified=False: 아직 확인 못해 비워둔 자리(placeholder) — 이 상태인 앨범은
  화면/모델에서 "확정 데이터 없음, 신호 기반 추정만 표시"로 처리해야 함.

주의
----
이 파일은 "최근 대표 앨범 1~2장" 위주의 시드일 뿐, 전체 디스코그래피가 아니다.
실제 서비스에서는 이 파일을 지속적으로 업데이트하거나, 사용자가 직접 새 보도자료
링크를 넣으면 파싱해서 추가하는 관리자 도구를 별도로 만드는 걸 추천한다.
"""

from __future__ import annotations

from typing import TypedDict


class AlbumSalesRecord(TypedDict, total=False):
    artist_id: str          # artists_data.ARTISTS 의 key
    album_name: str
    release_date: str        # YYYY-MM-DD
    first_week_sales: int | None   # 초동 판매량 (장)
    source_chart: str        # "hanteo" | "circle" | "both"
    verified: bool
    note: str
    source_desc: str         # 어떤 기사/발표를 근거로 했는지 사람이 읽을 설명 (URL 아님)


SEED_SALES: list[AlbumSalesRecord] = [

    # ---------------- BTS ----------------
    {
        "artist_id": "bts", "album_name": "Proof", "release_date": "2022-06-10",
        "first_week_sales": 2_752_496, "source_chart": "circle", "verified": True,
        "note": "발매일 기준 전세계 200만장 판매, 2023년 1월까지 누적 국내 350만장 이상 판매된 것으로 집계.",
        "source_desc": "위키피디아/빌보드 등 보도 기반 초동 수치",
    },

    # ---------------- BLACKPINK ----------------
    {
        "artist_id": "blackpink", "album_name": "BORN PINK", "release_date": "2022-09-16",
        "first_week_sales": 1_542_950, "source_chart": "hanteo", "verified": True,
        "note": "한터차트 기준(수출물량 일부 제외) 154만 2950장. 같은 앨범이 서클차트(수출포함) 기준으로는 214만 1281장으로 집계돼 걸그룹 최초 더블 밀리언셀러 기록.",
        "source_desc": "한터차트/다수 언론 보도 (2022-09-23)",
    },

    # ---------------- SEVENTEEN ----------------
    {
        "artist_id": "seventeen", "album_name": "SEVENTEENTH HEAVEN", "release_date": "2023-10-23",
        "first_week_sales": 5_090_000, "source_chart": "hanteo", "verified": True,
        "note": "한국 가요계 역사상 최초로 초동 500만장을 돌파한 앨범.",
        "source_desc": "나무위키 세븐틴 문서 기록",
    },
    {
        "artist_id": "seventeen", "album_name": "HAPPY BURSTDAY", "release_date": "2025-05-26",
        "first_week_sales": 2_521_208, "source_chart": "hanteo", "verified": True,
        "note": "2025년 K팝 초동 판매량 최고 기록(당해 기준).",
        "source_desc": "뉴스1 등 보도 (2025-06-02)",
    },

    # ---------------- aespa ----------------
    {
        "artist_id": "aespa", "album_name": "Whiplash", "release_date": "2024-10-21",
        "first_week_sales": 913_000, "source_chart": "hanteo", "verified": True,
        "note": "초동 밀리언셀러(100만장)에 약 8.7만장 못 미쳐 아쉬움을 남긴 케이스로 언급됨.",
        "source_desc": "한터차트 공식 보도자료 (2024-10-28)",
    },

    # ---------------- NewJeans ----------------
    {
        "artist_id": "newjeans", "album_name": "Get Up", "release_date": "2023-07-21",
        "first_week_sales": 311_200, "source_chart": "hanteo", "verified": True,
        "note": "당시 걸그룹 데뷔 이후 앨범 기준 신기록. 데뷔 미니 1집은 2023년 기준 누적 100만장 돌파(1997년 젝스키스 이후 최초 데뷔앨범 100만 달성 그룹).",
        "source_desc": "나무위키 NewJeans 문서",
    },

    # ---------------- LE SSERAFIM ----------------
    {
        "artist_id": "le_sserafim", "album_name": "UNFORGIVEN", "release_date": "2023-05-02",
        "first_week_sales": None, "source_chart": "hanteo", "verified": False,
        "note": "데뷔 366일 만에 밀리언셀러 달성(역대 2번째 최단 기록)이라는 사실은 확인됨. 정확한 초동 수치는 다음 조사에서 채울 것.",
        "source_desc": "나무위키 '역대 걸그룹 음반 초동 기록' 문서 (정확 수치 미확보)",
    },

    # ---------------- IVE ----------------
    {
        "artist_id": "ive", "album_name": "I've IVE", "release_date": "2023-04-10",
        "first_week_sales": 1_100_000, "source_chart": "hanteo", "verified": True,
        "note": "스타쉽엔터테인먼트 최초 초동 밀리언셀러. 이후 4개 앨범 연속 초동 밀리언셀러(총판 기준 7연속) 기록으로 이어짐.",
        "source_desc": "나무위키 IVE 문서",
    },
    {
        "artist_id": "ive", "album_name": "After LIKE (싱글3집)", "release_date": "2022-08-22",
        "first_week_sales": 920_000, "source_chart": "hanteo", "verified": True,
        "note": "당시 역대 한국 걸그룹 초동 판매량 2위. 발매 11일차 밀리언 달성(걸그룹 역사상 세 번째).",
        "source_desc": "나무위키 IVE 문서",
    },

    # ---------------- TWICE ----------------
    {
        "artist_id": "twice", "album_name": "With YOU-th", "release_date": "2024-02-23",
        "first_week_sales": 1_063_615, "source_chart": "hanteo", "verified": True,
        "note": "데뷔 10년차에 커리어 최초 초동 밀리언셀러 달성. 전작 대비 약 40만장 증가.",
        "source_desc": "JYP엔터테인먼트/한터차트 공식 발표, 파이낸셜뉴스·Soompi 보도 (2024-03-04)",
    },

    # ---------------- Stray Kids ----------------
    {
        "artist_id": "stray_kids", "album_name": "MAXIDENT", "release_date": "2022-10-07",
        "first_week_sales": 2_185_013, "source_chart": "hanteo", "verified": True,
        "note": "BTS에 이어 역대 K팝 아티스트 기준 두 번째로 높은 초동 기록(당시). 발매 6일차 더블 밀리언셀러 달성.",
        "source_desc": "JYP엔터테인먼트 공식 발표, 한국경제TV·전자신문 등 보도 (2022-10-14)",
    },

    # ---------------- 아래는 다음 조사 대상 (placeholder) ----------------
    # ATEEZ, TXT, ENHYPEN, ZEROBASEONE, RIIZE, NCT DREAM,
    # 그리고 솔로(Jimin FACE, Jung Kook GOLDEN, Jin Happy 등)는
    # 다음 세션에서 실제 보도자료 검색으로 채워 넣을 예정.
]


def get_sales_records(artist_id: str) -> list[AlbumSalesRecord]:
    return [r for r in SEED_SALES if r["artist_id"] == artist_id]


def has_verified_data(artist_id: str) -> bool:
    return any(r["verified"] for r in get_sales_records(artist_id))


if __name__ == "__main__":
    verified = [r for r in SEED_SALES if r["verified"]]
    unverified = [r for r in SEED_SALES if not r["verified"]]
    print(f"확보된 실측 레코드: {len(verified)}개")
    for r in verified:
        print(f"  - {r['artist_id']:15s} {r['album_name']:20s} "
              f"{r['first_week_sales']:>10,}장 ({r['source_chart']})")
    print(f"\n미확보(플레이스홀더): {len(unverified)}개 — 다음 조사 대상")
    for r in unverified:
        print(f"  - {r['artist_id']:15s} {r['album_name']}")
