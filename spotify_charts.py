"""
K-POP Comeback Radar — Spotify 글로벌 앨범 차트 실측 데이터

출처
----
Kaggle "Spotify Charts Daily Updated" (gonzalopezgil/spotify-charts-daily-updated)의
Weekly Top 200 Albums 파일 중 "global" 리전만 추출 → 우리 41개 아티스트로 필터링 →
앨범 단위로 집계한 결과.

이 데이터는 스포티파이 공식 위클리 앨범 차트(글로벌)를 그대로 반영한 실측치이며,
seed_sales.py(피지컬 판매량)와는 독립적인 "스트리밍 인기도" 신호다.

컬럼 설명
--------
best_global_rank   : 해당 앨범이 스포티파이 글로벌 위클리 앨범 차트에서 기록한 최고 순위 (낮을수록 좋음)
max_weeks_on_chart : 차트에 머문 최대 누적 주차 (스트리밍 지속력 지표)
release_date       : 앨범 발매일
entry_date          : 차트 최초 진입일
year                : release_date 기준 연도

한계
----
- "kr"(한국) 리전은 이 데이터셋에 아예 없어서 글로벌 리전만 사용했다.
- 41개 아티스트 중 17개만 매칭됨 — 나머지는 해당 기간 글로벌 앨범 Top 200에
  진입한 기록이 없거나(신인/인지도 낮음), 아티스트명 표기가 달라 매칭이 안 됐을 수 있다.
- 원본이 "누적 스트리밍 수"가 아니라 "차트 순위/체류 기간"이라, 정확한 스트리밍
  횟수가 필요하면 별도 소스가 필요하다.

아티스트 일간 차트(연도별 요약)
------------------------------
같은 Kaggle 데이터셋의 "Daily Top 200 Artists" 파일에서 글로벌 리전만 추출 →
연도별로 최고 순위(best_rank)/평균 순위(avg_rank)/차트 체류 일수(days_on_chart)를
집계한 결과. 앨범 단위가 아니라 "아티스트 인기도 자체"의 연도별 추이를 보여준다.
20개 아티스트, 2021~2026년 커버 (앨범 데이터보다 3개 아티스트 더 많이 매칭됨).
"""

from __future__ import annotations

import csv
import os
from typing import TypedDict


class SpotifyChartRecord(TypedDict):
    artist_id: str
    album_name: str
    best_global_rank: int
    max_weeks_on_chart: int
    release_date: str
    entry_date: str
    label: str
    year: int


class ArtistYearlyRecord(TypedDict):
    artist_id: str
    year: int
    best_rank: int
    avg_rank: float
    days_on_chart: int


_CSV_PATH = os.path.join(os.path.dirname(__file__), "spotify_global_album_charts_2020_2025.csv")
_ARTIST_YEARLY_CSV_PATH = os.path.join(os.path.dirname(__file__), "spotify_artist_yearly_2021_2026.csv")


def _load() -> list[SpotifyChartRecord]:
    if not os.path.exists(_CSV_PATH):
        return []
    records: list[SpotifyChartRecord] = []
    with open(_CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            records.append(
                {
                    "artist_id": row["artist_id"],
                    "album_name": row["album_name"],
                    "best_global_rank": int(row["best_global_rank"]),
                    "max_weeks_on_chart": int(row["max_weeks_on_chart"]),
                    "release_date": row["release_date"],
                    "entry_date": row["entry_date"],
                    "label": row["label"],
                    "year": int(row["year"]),
                }
            )
    return records


SPOTIFY_CHART_HISTORY: list[SpotifyChartRecord] = _load()


def _load_artist_yearly() -> list[ArtistYearlyRecord]:
    if not os.path.exists(_ARTIST_YEARLY_CSV_PATH):
        return []
    records: list[ArtistYearlyRecord] = []
    with open(_ARTIST_YEARLY_CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            records.append(
                {
                    "artist_id": row["artist_id"],
                    "year": int(row["year"]),
                    "best_rank": int(row["best_rank"]),
                    "avg_rank": float(row["avg_rank"]),
                    "days_on_chart": int(row["days_on_chart"]),
                }
            )
    return records


ARTIST_YEARLY_HISTORY: list[ArtistYearlyRecord] = _load_artist_yearly()


def get_artist_yearly_history(artist_id: str) -> list[ArtistYearlyRecord]:
    """특정 아티스트의 연도별 글로벌 인기도 추이(최고순위/평균순위/차트 체류일)를 연도순으로 반환."""
    rows = [r for r in ARTIST_YEARLY_HISTORY if r["artist_id"] == artist_id]
    return sorted(rows, key=lambda r: r["year"])


def has_artist_yearly_data(artist_id: str) -> bool:
    return any(r["artist_id"] == artist_id for r in ARTIST_YEARLY_HISTORY)


def latest_artist_trend(artist_id: str) -> ArtistYearlyRecord | None:
    """가장 최근 연도의 인기도 스냅샷 (없으면 None)."""
    rows = get_artist_yearly_history(artist_id)
    return rows[-1] if rows else None


def get_chart_history(artist_id: str) -> list[SpotifyChartRecord]:
    """특정 아티스트의 글로벌 앨범 차트 실측 이력을 발매일 순으로 반환."""
    rows = [r for r in SPOTIFY_CHART_HISTORY if r["artist_id"] == artist_id]
    return sorted(rows, key=lambda r: r["release_date"])


def has_chart_data(artist_id: str) -> bool:
    return any(r["artist_id"] == artist_id for r in SPOTIFY_CHART_HISTORY)


def best_rank_ever(artist_id: str) -> int | None:
    rows = get_chart_history(artist_id)
    return min((r["best_global_rank"] for r in rows), default=None)


if __name__ == "__main__":
    artists = sorted({r["artist_id"] for r in SPOTIFY_CHART_HISTORY})
    print(f"[앨범 차트] 실측 데이터 확보된 아티스트: {len(artists)}개")
    for aid in artists:
        rows = get_chart_history(aid)
        best = best_rank_ever(aid)
        print(f"  {aid:15s} 앨범 {len(rows)}개, 역대 최고 글로벌 순위 {best}위")

    yearly_artists = sorted({r["artist_id"] for r in ARTIST_YEARLY_HISTORY})
    print(f"\n[아티스트 연도별 인기도] 실측 데이터 확보된 아티스트: {len(yearly_artists)}개")
    for aid in yearly_artists:
        latest = latest_artist_trend(aid)
        print(f"  {aid:15s} 최신({latest['year']}) 최고순위 {latest['best_rank']}위, "
              f"평균순위 {latest['avg_rank']}, 차트체류 {latest['days_on_chart']}일")
