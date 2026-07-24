"""
K-POP Comeback Radar — 판매량/수익 예측 모델 (v1 설계)

왜 "진짜 ML"이 아니라 하이브리드로 시작하는가
--------------------------------------------
지도학습(회귀/그래디언트부스팅 등)이 의미 있으려면 최소 수십~수백 개의
(피처, 정답 초동 판매량) 쌍이 필요하다. 지금 우리가 실측 확보한 건 6개뿐이라
바로 회귀모델을 학습시키면 사실상 6개 포인트에 과적합된 장난감 모델이 된다.

그래서 v1은:
  1) 그룹별 "기준선(baseline)" — 하나증권 리포트 등 공개 자료가 보여준
     2021~2022년 그룹 간 상대적 초동 순위 + 우리가 확보한 실측치를 앵커로 사용
  2) "신호 배수(signal multiplier)" — 이번 컴백의 사전 신호(스트리밍 인기도
     추세, 유튜브 조회수 모멘텀, 뉴스 버즈량, 컴백 간격)를 곱해서 조정
  3) 결과는 항상 "단일 숫자"가 아니라 "구간(band)"으로 제시 + 신뢰도 라벨

이렇게 하면 최소 30~50개 이상의 검증된 실측 레코드가 쌓였을 때
gradient boosting(예: LightGBM) 등으로 자연스럽게 업그레이드할 수 있는
피처 파이프라인을 지금부터 동일하게 맞춰둘 수 있다. (아래 build_feature_vector 참고)

수익(금액) 환산에 대한 정직한 경고
----------------------------------
음반 1장당 실제 순이익은 유통 마진, 프로모션 앨범(무료 배포분), 특전 경쟁
등으로 기획사마다 다르고 비공개다. 여기서 제시하는 "예상 수익"은 업계에
공개적으로 논의되는 대략적 벤치마치(음반 평균가, 스트리밍 곡당 정산액 등)를
적용한 "일러스트레이션"이지 회계적으로 검증된 수치가 아니다. UI에도 반드시
"추정치, 실제 정산과 다를 수 있음" 문구를 노출해야 한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from spotify_charts import has_chart_data, best_rank_ever, has_artist_yearly_data

# =========================================================
# 1. 그룹 기준선(baseline) — 공개 리포트 + 확보한 실측치 기반 앵커
# =========================================================
# 단위: 만장(10,000장). 하나증권 리포트(2022) 상대순위 + 우리가 검색으로 확보한
# 실측치를 조합한 "출발점"이며, 새 실측 데이터가 들어올 때마다 갱신해야 한다.

GROUP_BASELINE_MANJANG: dict[str, float] = {
    # 실측 확보(seed_sales.py) — 최근 대표작 기준
    "bts": 275.0,            # Proof 초동 (2022) 참고, 최근작 기준 추정 필요
    "seventeen": 350.0,      # 최근 2개 앨범 평균(509만/252만)
    "blackpink": 154.0,
    "aespa": 91.0,
    "newjeans": 50.0,        # 데뷔 초기 대비 최근 활동 반영 하향 조정 필요(분쟁 이슈)
    "le_sserafim": 130.0,    # 미확보 — 유사 티어(하나증권 리포트상 상위권) 참고 추정치
    "ive": 100.0,            # 실측: I've IVE 110만 / After LIKE 92만 평균
    "twice": 106.0,          # 실측: With YOU-th 초동 1,063,615장

    # 미확보 — 2022년 하나증권 리포트의 상대 순위만 반영한 잠정 추정치
    # (실측 조사 완료되면 이 값을 대체할 것)
    "itzy": 60.0,
    "red_velvet": 55.0,
    "gidle": 40.0,
    "nmixx": 25.0,
    "staych": 20.0,
    "kep1er": 30.0,

    "nct_dream": 150.0,
    "txt": 140.0,
    "enhypen": 120.0,
    "nct_127": 100.0,
    "stray_kids": 218.0,     # 실측: MAXIDENT 초동 2,185,013장
    "ateez": 90.0,
    "zb1": 130.0,
    "riize": 60.0,
    "boynextdoor": 40.0,

    # 솔로 — 그룹 대비 현저히 낮은 게 일반적 (팬덤이 그룹으로 분산)
    "jimin": 100.0, "jin": 80.0, "agust_d": 40.0, "jhope": 35.0,
    "v": 70.0, "jungkook": 60.0, "rm": 30.0,
    "jennie": 30.0, "jisoo": 20.0, "rose": 25.0, "lisa": 20.0,
    "nayeon": 15.0, "jihyo": 10.0, "wendy": 8.0, "seulgi": 8.0, "soyeon": 10.0,
}

CONFIDENCE_HAS_SEED = {
    "bts", "seventeen", "blackpink", "aespa", "newjeans",
    "ive", "twice", "stray_kids",
}

# 피지컬 판매량 실측이 없어도, 스포티파이 글로벌 앨범 차트 실측 또는 아티스트
# 연도별 인기도 실측(spotify_charts.py)이 있으면 "완전 추정(low)"보다는 한 단계 위로 취급한다.
CONFIDENCE_HAS_STREAM_SEED = {
    aid for aid in GROUP_BASELINE_MANJANG
    if has_chart_data(aid) or has_artist_yearly_data(aid)
} - CONFIDENCE_HAS_SEED


@dataclass
class SignalInputs:
    """이번 컴백 직전/직후 관측 가능한 신호. main.py 의 기존 계산 로직과 연결됨."""
    apple_popularity_score: float      # 0-100, normalize_popularity() 재사용
    youtube_view_momentum: float       # 0-100, 최근 영상 조회수 증가율 정규화
    news_buzz_score: float             # 0-100, 글로벌+국내 뉴스 언급량 정규화
    days_since_last_comeback: int | None
    album_format: Literal["정규", "미니", "싱글", "리패키지"] = "미니"


@dataclass
class SalesPrediction:
    artist_id: str
    low: int
    mid: int
    high: int
    confidence: Literal["high", "medium", "low"]
    explanation: str


# =========================================================
# 2. 신호 배수 계산
# =========================================================

def _format_multiplier(fmt: str) -> float:
    # 정규 앨범은 통상 미니보다 팬덤 구매력이 크게 반영되는 경향(실물 특전 다양화 등)
    return {"정규": 1.15, "미니": 1.0, "싱글": 0.55, "리패키지": 0.75}.get(fmt, 1.0)


def _cadence_multiplier(days_since_last: int | None) -> float:
    """컴백 간격이 너무 짧으면(피로도) 소폭 하향, 적당히 길면(기대감 누적) 소폭 상향."""
    if days_since_last is None:
        return 1.0
    if days_since_last < 90:
        return 0.92
    if days_since_last <= 240:
        return 1.05
    if days_since_last <= 400:
        return 1.10
    return 1.0  # 너무 오래 쉬면 팬덤 이탈 리스크도 있어 추가 상향은 보수적으로 제한


def compute_signal_multiplier(signals: SignalInputs) -> float:
    """세 신호(0-100)를 가중 평균해 0.6~1.4 범위의 배수로 변환."""
    weighted = (
        signals.apple_popularity_score * 0.35
        + signals.youtube_view_momentum * 0.40
        + signals.news_buzz_score * 0.25
    )
    # 50점을 "평상시(배수 1.0)"으로 두고 선형 매핑
    base_multiplier = 0.6 + (weighted / 100) * 0.8
    return base_multiplier * _format_multiplier(signals.album_format) * _cadence_multiplier(
        signals.days_since_last_comeback
    )


# =========================================================
# 3. 예측 함수
# =========================================================

def predict_first_week_sales(artist_id: str, signals: SignalInputs) -> SalesPrediction:
    baseline = GROUP_BASELINE_MANJANG.get(artist_id)
    if baseline is None:
        # 데이터베이스에 없는 신규/소규모 아티스트는 극도로 보수적인 최소 추정만 제공
        baseline = 5.0
        confidence: Literal["high", "medium", "low"] = "low"
    elif artist_id in CONFIDENCE_HAS_SEED and (has_chart_data(artist_id) or has_artist_yearly_data(artist_id)):
        # 피지컬 판매량 실측 + 스포티파이 실측(앨범 차트 또는 연도별 인기도)이 둘 다 있는 경우
        confidence = "high"
    elif artist_id in CONFIDENCE_HAS_SEED or artist_id in CONFIDENCE_HAS_STREAM_SEED:
        confidence = "medium"
    else:
        confidence = "low"

    multiplier = compute_signal_multiplier(signals)
    mid_manjang = baseline * multiplier
    # 구간 폭은 신뢰도가 낮을수록 넓힌다 (불확실성을 정직하게 반영)
    spread = {"high": 0.15, "medium": 0.25, "low": 0.40}[confidence]

    mid = int(mid_manjang * 10_000)
    low = int(mid_manjang * (1 - spread) * 10_000)
    high = int(mid_manjang * (1 + spread) * 10_000)

    rank_note = ""
    if has_chart_data(artist_id):
        rank = best_rank_ever(artist_id)
        rank_note = f", 스포티파이 글로벌 최고 {rank}위 실측 반영"

    explanation = (
        f"기준선 {baseline:.0f}만장 × 신호배수 {multiplier:.2f} "
        f"(신뢰도: {confidence}{rank_note})"
    )
    return SalesPrediction(artist_id, low, mid, high, confidence, explanation)


# =========================================================
# 4. 수익(금액) 환산 — 반드시 "추정치" 라벨과 함께 노출할 것
# =========================================================

@dataclass
class RevenueAssumptions:
    """튜닝 가능한 가정치. UI에 이 값들을 그대로 노출해서 사용자가 직접
    바꿔볼 수 있게 하면(예: 슬라이더) 훨씬 더 정직한 도구가 된다."""
    avg_physical_album_price_krw: int = 25_000       # 소비자가 평균(버전 다양화 고려 보수적 값)
    label_net_margin_ratio: float = 0.35             # 유통/제작비 제외 후 기획사 순이익 비중(추정)
    est_streams_per_physical_buyer: int = 15         # 앨범 구매자 1인당 평균 스트리밍 횟수(추정)
    revenue_per_stream_krw: float = 4.0              # 스트리밍 1회당 정산액 추정(플랫폼/계약마다 상이)


def estimate_revenue_band(sales: SalesPrediction, assumptions: RevenueAssumptions | None = None) -> dict:
    a = assumptions or RevenueAssumptions()

    def _one(units: int) -> dict:
        physical_revenue = units * a.avg_physical_album_price_krw * a.label_net_margin_ratio
        streaming_revenue = (
            units * a.est_streams_per_physical_buyer * a.revenue_per_stream_krw
        )
        return {
            "physical_krw": int(physical_revenue),
            "streaming_krw": int(streaming_revenue),
            "total_krw": int(physical_revenue + streaming_revenue),
        }

    return {
        "low": _one(sales.low),
        "mid": _one(sales.mid),
        "high": _one(sales.high),
        "disclaimer": (
            "이 금액은 공개된 업계 벤치마치 가정치를 적용한 추정 일러스트레이션입니다. "
            "실제 기획사 정산 구조·유통 계약·프로모션 앨범 비중에 따라 크게 달라질 수 있습니다."
        ),
    }


# =========================================================
# 5. 실행 예시
# =========================================================

if __name__ == "__main__":
    signals = SignalInputs(
        apple_popularity_score=82,
        youtube_view_momentum=74,
        news_buzz_score=68,
        days_since_last_comeback=210,
        album_format="미니",
    )
    pred = predict_first_week_sales("aespa", signals)
    print(f"[{pred.artist_id}] 예상 초동: {pred.low:,} ~ {pred.high:,}장 (중앙값 {pred.mid:,}장)")
    print(f"  근거: {pred.explanation}")

    revenue = estimate_revenue_band(pred)
    print(f"  예상 수익(중앙값): 약 {revenue['mid']['total_krw']:,}원")
    print(f"  ({revenue['disclaimer']})")
