"""
K-POP Comeback Radar v2
========================
아이튠즈/애플뮤직 무드로 리디자인 + 그룹·솔로 분리 + 판매량 예측 + 컴백 빈도 분석.

같은 폴더에 artists_data.py / seed_sales.py / prediction_model.py 가 있어야 합니다.
"""

from __future__ import annotations

import html
import math
import re
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from artists_data import ARTISTS, get_display_options
from seed_sales import get_sales_records, has_verified_data
from spotify_charts import get_chart_history, has_chart_data
from prediction_model import (
    SignalInputs,
    predict_first_week_sales,
    estimate_revenue_band,
    RevenueAssumptions,
)


# =========================================================
# 1. PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="K-POP Comeback Radar",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 2. API ENDPOINTS
# =========================================================

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
MEDIASTACK_API_URL = "http://api.mediastack.com/v1/news"
NAVER_NEWS_API_URL = "https://openapi.naver.com/v1/search/news.json"
SOLAR_CHAT_API_URL = "https://api.upstage.ai/v1/solar/chat/completions"


# =========================================================
# 3. DESIGN TOKENS — iTunes / Apple Music 무드
# =========================================================
# 팔레트: 애플뮤직 실제 브랜드 그라데이션(마젠타→레드→오렌지)을 다크 베이스 위에 얹었다.
#   --bg        #0b0b0f  (거의 검정, 완전한 검정은 피해 깊이감 유지)
#   --card      #16161d  (카드 배경)
#   --accent1   #fa233b  (Apple Music red)
#   --accent2   #fb5c74  (mid pink)
#   --accent3   #ff9500  (warm orange, 앨범 커버 하이라이트에도 자주 쓰이는 톤)
#   --spotify   #1db954  (스트리밍 신호에만 아주 절제해서 사용 — 두 플랫폼 무드를 살짝 교차)
# 타이포: 디스플레이 = SF Pro Display(시스템), 본문 = Pretendard(한글 가독성),
#         데이터/차트 숫자 = ui-monospace — "차트 터미널" 느낌을 숫자에만 부여.
# 시그니처: 헤더의 이퀄라이저 바 애니메이션 — 컴백 스코어가 높을수록 바가 더 빠르고 높게 움직인다.

st.markdown(
    """
    <style>
        :root {
            --bg: #0b0b0f;
            --card: #16161d;
            --card-border: rgba(255,255,255,.08);
            --ink: #f2f2f5;
            --muted: #8c8c99;
            --accent1: #ff2d55;
            --accent2: #ff5f8f;
            --accent3: #ffaa00;
            --spotify: #1db954;
            --sidebar-bg: #f5f5f7;
            --sidebar-ink: #111114;
        }

        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                "Pretendard", "Noto Sans KR", sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 0%, rgba(255,45,85,.22), transparent 34%),
                radial-gradient(circle at 88% 6%, rgba(255,170,0,.18), transparent 32%),
                radial-gradient(circle at 50% 100%, rgba(255,95,143,.10), transparent 40%),
                var(--bg);
            color: var(--ink);
        }

        .block-container { max-width: 1440px; padding-top: 1.6rem; padding-bottom: 3rem; }

        /* ---------- 사이드바: 밝은 배경 + 검정 텍스트 (아이튠즈 클래식 톤) ---------- */
        [data-testid="stSidebar"] {
            background: var(--sidebar-bg);
            border-right: 1px solid rgba(0,0,0,.08);
        }
        [data-testid="stSidebar"] * {
            color: var(--sidebar-ink) !important;
        }
        [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
            background: #ffffff;
            border-radius: 10px;
        }
        [data-testid="stSidebar"] hr { border-color: rgba(0,0,0,.12) !important; }

        .mono { font-family: ui-monospace, "SF Mono", "Menlo", monospace; }

        /* ---------- 시그니처: 이퀄라이저 바 ---------- */
        .eq-bars {
            display: inline-flex;
            align-items: flex-end;
            gap: 3px;
            height: 18px;
            margin-left: 10px;
            vertical-align: middle;
        }
        .eq-bars span {
            display: block;
            width: 3px;
            border-radius: 2px;
            background: linear-gradient(180deg, var(--accent3), var(--accent1));
            animation: eq-bounce ease-in-out infinite;
        }
        @keyframes eq-bounce {
            0%, 100% { height: 4px; }
            50% { height: 16px; }
        }

        .hero {
            position: relative;
            overflow: hidden;
            padding: 34px 38px;
            margin-bottom: 22px;
            border-radius: 26px;
            border: 1px solid var(--card-border);
            background:
                linear-gradient(120deg, rgba(255,45,85,.28), rgba(255,170,0,.16)),
                var(--card);
            box-shadow: 0 0 60px rgba(255,45,85,.10);
        }
        .eyebrow {
            background: linear-gradient(90deg, #fff, var(--accent2) 60%, var(--accent3));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 2.4rem; font-weight: 900; letter-spacing: -.02em;
            text-transform: uppercase; margin-bottom: 10px; line-height: 1.1;
        }
        .hero-title {
            font-size: clamp(1.05rem, 2vw, 1.8rem);
            font-weight: 800; letter-spacing: -.02em; margin: 0;
            color: #fff;
        }
        .hero-subtitle { color: var(--muted); margin-top: 12px; max-width: 820px; line-height: 1.6; }

        .section-title {
            font-size: 1.22rem; font-weight: 800; margin: 18px 0 12px;
            display: flex; align-items: center; gap: 8px;
        }

        .glass-card {
            height: 100%; padding: 20px; border-radius: 18px;
            background: var(--card); border: 1px solid var(--card-border);
        }

        .album-card {
            display: flex; gap: 18px; align-items: center; padding: 18px;
            border-radius: 18px; background: var(--card); border: 1px solid var(--card-border);
            margin-bottom: 14px;
        }
        .album-cover {
            width: 112px; height: 112px; min-width: 112px; border-radius: 14px;
            object-fit: cover; background: #24242c;
            box-shadow: 0 10px 26px rgba(0,0,0,.5);
        }
        .album-name { font-size: 1.08rem; font-weight: 800; margin: 6px 0; color: #fff; }
        .muted { color: var(--muted); font-size: .89rem; line-height: 1.55; }

        .score-card {
            text-align: center; padding: 26px 18px; border-radius: 20px;
            background: radial-gradient(circle at 50% 0%, rgba(250,35,59,.22), transparent 45%), var(--card);
            border: 1px solid var(--card-border);
        }
        .score-number {
            font-family: ui-monospace, "SF Mono", monospace;
            font-size: 3.6rem; font-weight: 800;
            background: linear-gradient(90deg, var(--accent2), var(--accent3));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .news-card {
            padding: 15px 16px; margin-bottom: 10px; border-radius: 15px;
            background: var(--card); border: 1px solid var(--card-border);
        }
        .news-title { color: #fff; font-weight: 700; font-size: .95rem; text-decoration: none; }
        .news-title:hover { color: var(--accent2); }
        .news-meta { color: var(--muted); font-size: .76rem; margin-top: 7px; }

        .badge {
            display: inline-block; padding: 4px 10px; border-radius: 999px;
            font-size: .72rem; font-weight: 700; margin: 2px 4px 2px 0;
            background: rgba(250,35,59,.14); border: 1px solid rgba(251,92,116,.28);
            color: #ffd7dc;
        }
        .badge-spotify {
            background: rgba(29,185,84,.14); border: 1px solid rgba(29,185,84,.32); color: #b7f5cd;
        }
        .badge-solo {
            background: rgba(255,149,0,.14); border: 1px solid rgba(255,149,0,.32); color: #ffe0b3;
        }

        .revenue-band {
            padding: 18px; border-radius: 16px; background: var(--card);
            border: 1px solid var(--card-border); text-align: center;
        }
        .revenue-band .val {
            font-family: ui-monospace, "SF Mono", monospace;
            font-size: 1.5rem; font-weight: 800; color: #fff;
        }
        .revenue-band .lbl { color: var(--muted); font-size: .78rem; margin-top: 4px; }

        .verified-tag {
            display: inline-block; padding: 3px 9px; border-radius: 8px;
            background: rgba(29,185,84,.16); color: #7fe6a6; font-size: .72rem; font-weight: 800;
        }
        .estimate-tag {
            display: inline-block; padding: 3px 9px; border-radius: 8px;
            background: rgba(255,149,0,.16); color: #ffcb80; font-size: .72rem; font-weight: 800;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(90deg, var(--accent1), var(--accent3));
            color: #fff; border: 0; border-radius: 12px; font-weight: 800;
        }

        hr { border-color: var(--card-border) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_eq_bars(intensity: float) -> str:
    """intensity(0-100)에 따라 바 개수/속도/높이가 달라지는 이퀄라이저를 렌더링."""
    intensity = max(0.0, min(100.0, intensity))
    bar_count = 4 + int(intensity / 100 * 4)  # 4~8개
    bars = []
    for i in range(bar_count):
        duration = 1.4 - (intensity / 100) * 0.9 - (i % 3) * 0.08
        duration = max(duration, 0.35)
        delay = (i % 4) * 0.12
        bars.append(
            f'<span style="animation-duration:{duration:.2f}s;'
            f'animation-delay:{delay:.2f}s;"></span>'
        )
    return f'<span class="eq-bars">{"".join(bars)}</span>'


# =========================================================
# 4. HELPERS
# =========================================================

def get_secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


def safe_request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = 20,
) -> dict[str, Any]:
    try:
        response = requests.request(method=method, url=url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout as exc:
        raise RuntimeError("API 응답 시간이 초과되었습니다.") from exc
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise RuntimeError(f"HTTP {status}") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"네트워크 요청 실패: {exc}") from exc


def escape_text(value: Any) -> str:
    return html.escape(str(value or ""))


def strip_html_tags(value: str | None) -> str:
    if not value:
        return ""
    return html.unescape(re.sub(r"<[^>]+>", "", value)).strip()


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    formats = (None, "%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%d")
    for date_format in formats:
        try:
            parsed = (
                datetime.fromisoformat(value.replace("Z", "+00:00"))
                if date_format is None
                else datetime.strptime(value, date_format)
            )
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except (ValueError, TypeError):
            continue
    return None


def format_date(value: str | None) -> str:
    parsed = parse_datetime(value)
    return parsed.astimezone().strftime("%Y.%m.%d") if parsed else "-"


def days_since(value: str | None) -> int | None:
    parsed = parse_datetime(value)
    if not parsed:
        return None
    return max((datetime.now(timezone.utc) - parsed.astimezone(timezone.utc)).days, 0)


def format_number(value: int | float | str | None) -> str:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return "-"
    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    if number >= 1_000:
        return f"{number / 1_000:.1f}K"
    return f"{int(number):,}"


def normalize_youtube_views(value: int | float | None) -> float:
    try:
        views = max(float(value or 0), 0)
    except (TypeError, ValueError):
        views = 0
    return min(math.log10(views + 1) / 8 * 100, 100) if views else 0.0


def freshness_score(release_date: str | None) -> float:
    age = days_since(release_date)
    if age is None:
        return 0.0
    if age <= 7:
        return 100.0
    if age <= 30:
        return 90.0
    if age <= 60:
        return 75.0
    if age <= 90:
        return 60.0
    if age <= 180:
        return 40.0
    if age <= 365:
        return 20.0
    return 5.0


def score_label(score: float) -> str:
    if score >= 85:
        return "🔥 초강력 컴백 신호"
    if score >= 70:
        return "🚀 높은 관심도"
    if score >= 55:
        return "✨ 상승 신호 감지"
    if score >= 40:
        return "🌙 관심도 관찰 중"
    return "📡 레이더 탐색 중"


def artist_name_matches(result_artist: str, target_artist: str) -> bool:
    result = re.sub(r"[^a-z0-9가-힣]", "", result_artist.casefold())
    target = re.sub(r"[^a-z0-9가-힣]", "", target_artist.casefold())
    return result == target or target in result or result in target


# =========================================================
# 5. APPLE ITUNES SEARCH API
# =========================================================

@st.cache_data(ttl=1800, show_spinner=False)
def get_apple_music_data(artist_query: str) -> dict[str, Any]:
    album_result = safe_request(
        "GET", ITUNES_SEARCH_URL,
        params={"term": artist_query, "country": "KR", "media": "music",
                "entity": "album", "attribute": "artistTerm", "limit": 50},
    )
    track_result = safe_request(
        "GET", ITUNES_SEARCH_URL,
        params={"term": artist_query, "country": "KR", "media": "music",
                "entity": "musicTrack", "attribute": "artistTerm", "limit": 50},
    )

    raw_albums = album_result.get("results", [])
    raw_tracks = track_result.get("results", [])

    albums = [a for a in raw_albums if artist_name_matches(a.get("artistName", ""), artist_query)]
    tracks = [t for t in raw_tracks if artist_name_matches(t.get("artistName", ""), artist_query)]

    if not albums and not tracks:
        raise RuntimeError("Apple 카탈로그에서 아티스트 데이터를 찾지 못했습니다.")

    unique_albums: list[dict[str, Any]] = []
    seen: set[str] = set()
    for album in albums:
        key = str(album.get("collectionId") or album.get("collectionName", "")).strip()
        if key and key not in seen:
            seen.add(key)
            unique_albums.append(album)
    unique_albums.sort(key=lambda a: a.get("releaseDate", ""), reverse=True)

    latest = unique_albums[0] if unique_albums else {}
    selected_tracks = tracks[:10]
    artwork = latest.get("artworkUrl100", "")
    artwork_hi = artwork.replace("100x100bb", "600x600bb") if artwork else ""

    return {
        "artist": {
            "name": latest.get("artistName") or (selected_tracks[0].get("artistName") if selected_tracks else artist_query),
            "genre": latest.get("primaryGenreName") or "K-Pop",
            "catalog_albums": len(unique_albums),
            "catalog_tracks": len(tracks),
            "artist_url": latest.get("artistViewUrl", ""),
        },
        "latest_album": {
            "name": latest.get("collectionName", "앨범 정보 없음"),
            "release_date": latest.get("releaseDate", ""),
            "album_type": latest.get("collectionType", "Album"),
            "total_tracks": latest.get("trackCount", 0),
            "image": artwork_hi,
            "apple_url": latest.get("collectionViewUrl", ""),
        },
        "tracks": [
            {"name": t.get("trackName", ""), "album": t.get("collectionName", ""),
             "release_date": t.get("releaseDate", ""), "duration_ms": t.get("trackTimeMillis", 0),
             "preview_url": t.get("previewUrl", ""), "apple_url": t.get("trackViewUrl", ""),
             "track_number": t.get("trackNumber", 0)}
            for t in selected_tracks
        ],
        "albums": [
            {"name": a.get("collectionName", ""), "release_date": a.get("releaseDate", ""),
             "track_count": a.get("trackCount", 0), "apple_url": a.get("collectionViewUrl", "")}
            for a in unique_albums[:30]
        ],
    }


# =========================================================
# 6. YOUTUBE
# =========================================================

@st.cache_data(ttl=1800, show_spinner=False)
def get_youtube_data(search_query: str, api_key: str) -> list[dict[str, Any]]:
    search_result = safe_request(
        "GET", f"{YOUTUBE_API_URL}/search",
        params={"part": "snippet", "q": search_query, "type": "video",
                "order": "date", "maxResults": 8, "key": api_key},
    )
    video_ids = [i.get("id", {}).get("videoId") for i in search_result.get("items", []) if i.get("id", {}).get("videoId")]
    if not video_ids:
        return []

    detail_result = safe_request(
        "GET", f"{YOUTUBE_API_URL}/videos",
        params={"part": "snippet,statistics", "id": ",".join(video_ids), "key": api_key},
    )
    videos = []
    for item in detail_result.get("items", []):
        snippet, stats = item.get("snippet", {}), item.get("statistics", {})
        thumbs = snippet.get("thumbnails", {})
        vid = item.get("id", "")
        videos.append({
            "video_id": vid,
            "title": html.unescape(snippet.get("title", "")),
            "published_at": snippet.get("publishedAt", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "thumbnail": thumbs.get("high", {}).get("url") or thumbs.get("medium", {}).get("url") or "",
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "comments": int(stats.get("commentCount", 0)),
            "url": f"https://www.youtube.com/watch?v={vid}",
        })
    videos.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    return videos


# =========================================================
# 7. NEWS
# =========================================================

@st.cache_data(ttl=1800, show_spinner=False)
def get_global_news(query: str, api_key: str) -> list[dict[str, Any]]:
    result = safe_request(
        "GET", MEDIASTACK_API_URL,
        params={"access_key": api_key, "keywords": query, "languages": "en",
                "sort": "published_desc", "limit": 10, "offset": 0},
    )
    if result.get("error"):
        error = result["error"]
        raise RuntimeError(f"{error.get('code', 'unknown_error')}: {error.get('message', 'Mediastack 오류')}")
    return [
        {"title": a.get("title", ""), "description": a.get("description", ""),
         "source": a.get("source", ""), "published_at": a.get("published_at", ""),
         "url": a.get("url", ""), "channel": "Global"}
        for a in result.get("data", []) if a.get("title") and a.get("url")
    ]


@st.cache_data(ttl=1800, show_spinner=False)
def get_naver_news(query: str, client_id: str, client_secret: str) -> list[dict[str, Any]]:
    result = safe_request(
        "GET", NAVER_NEWS_API_URL,
        headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret},
        params={"query": query, "display": 10, "start": 1, "sort": "date"},
    )
    return [
        {"title": strip_html_tags(i.get("title")), "description": strip_html_tags(i.get("description")),
         "source": "네이버 뉴스", "published_at": i.get("pubDate", ""),
         "url": i.get("originallink") or i.get("link", ""), "channel": "Korea"}
        for i in result.get("items", [])
    ]


# =========================================================
# 8. DEMO DATA
# =========================================================

def get_demo_bundle(artist_name: str) -> dict[str, Any]:
    today = datetime.now(timezone.utc).isoformat()
    return {
        "apple": {
            "artist": {"name": artist_name, "genre": "K-Pop", "catalog_albums": 12,
                       "catalog_tracks": 42, "artist_url": ""},
            "latest_album": {"name": f"{artist_name} Demo Album", "release_date": today,
                             "album_type": "Album", "total_tracks": 8, "image": "", "apple_url": ""},
            "tracks": [
                {"name": "Demo Track A", "album": "Demo Album", "release_date": today,
                 "duration_ms": 192000, "preview_url": "", "apple_url": "", "track_number": 1},
                {"name": "Demo Track B", "album": "Demo Album", "release_date": today,
                 "duration_ms": 205000, "preview_url": "", "apple_url": "", "track_number": 2},
            ],
            "albums": [
                {"name": f"{artist_name} EP {i}", "release_date": today, "track_count": 6, "apple_url": ""}
                for i in range(1, 6)
            ],
        },
        "youtube": [
            {"video_id": "", "title": f"{artist_name} Official MV — Demo", "published_at": today,
             "channel_title": f"{artist_name} Official", "thumbnail": "", "views": 48_500_000,
             "likes": 2_450_000, "comments": 185_000, "url": ""},
        ],
        "global_news": [
            {"title": f"{artist_name} draws global attention with a new comeback",
             "description": "Demo global news data.", "source": "Demo Global News",
             "published_at": today, "url": "", "channel": "Global"}
        ],
        "naver_news": [
            {"title": f"{artist_name}, 컴백 기대감 높이는 새로운 콘텐츠 공개",
             "description": "국내 데모 뉴스입니다.", "source": "네이버 뉴스 데모",
             "published_at": today, "url": "", "channel": "Korea"}
        ],
    }


# =========================================================
# 9. COMEBACK SCORE
# =========================================================

def calculate_comeback_score(
    apple_data: dict[str, Any],
    youtube_data: list[dict[str, Any]],
    global_news: list[dict[str, Any]],
    naver_news: list[dict[str, Any]],
) -> tuple[float, dict[str, float]]:
    release_score = freshness_score(apple_data.get("latest_album", {}).get("release_date"))
    catalog_tracks = apple_data.get("artist", {}).get("catalog_tracks", 0)
    catalog_score = min(float(catalog_tracks) / 50 * 100, 100)
    top_views = max((v.get("views", 0) for v in youtube_data), default=0)
    youtube_score = normalize_youtube_views(top_views)
    recent_global = sum(1 for a in global_news if (age := days_since(a.get("published_at"))) is not None and age <= 30)
    recent_korean = sum(1 for a in naver_news if (age := days_since(a.get("published_at"))) is not None and age <= 30)
    global_score = min(recent_global / 10 * 100, 100)
    korean_score = min(recent_korean / 10 * 100, 100)

    components = {
        "발매 최신성": round(release_score, 1),
        "YouTube 반응": round(youtube_score, 1),
        "글로벌 뉴스": round(global_score, 1),
        "국내 뉴스": round(korean_score, 1),
        "Apple 카탈로그": round(catalog_score, 1),
    }
    total = (
        components["발매 최신성"] * 0.30 + components["YouTube 반응"] * 0.35
        + components["글로벌 뉴스"] * 0.15 + components["국내 뉴스"] * 0.15
        + components["Apple 카탈로그"] * 0.05
    )
    return round(total, 1), components


# =========================================================
# 10. NEW — 컴백/발매 빈도 분석 (맥루머 스타일)
# =========================================================

def classify_format(track_count: int) -> str:
    if track_count <= 0:
        return "미상"
    if track_count == 1:
        return "디지털 싱글"
    if track_count <= 3:
        return "싱글 앨범"
    if track_count <= 8:
        return "미니 앨범"
    return "정규 앨범"


def analyze_release_cadence(albums: list[dict[str, Any]]) -> dict[str, Any]:
    """앨범/싱글 발매 이력을 바탕으로 컴백 간격을 분석한다."""
    parsed = []
    for a in albums:
        dt = parse_datetime(a.get("release_date"))
        if dt:
            parsed.append((dt, a))
    parsed.sort(key=lambda x: x[0])

    if len(parsed) < 2:
        return {
            "avg_gap_days": None, "min_gap_days": None, "max_gap_days": None,
            "release_count_last_year": len(parsed), "format_counts": {}, "timeline": parsed,
        }

    gaps = [(parsed[i][0] - parsed[i - 1][0]).days for i in range(1, len(parsed))]
    one_year_ago = datetime.now(timezone.utc) - (parsed[-1][0] - parsed[-1][0])  # placeholder, replaced below
    now = datetime.now(timezone.utc)
    release_count_last_year = sum(
        1 for dt, _ in parsed if (now - dt.astimezone(timezone.utc)).days <= 365
    )
    format_counts: dict[str, int] = {}
    for _, a in parsed:
        fmt = classify_format(a.get("track_count", 0))
        format_counts[fmt] = format_counts.get(fmt, 0) + 1

    return {
        "avg_gap_days": round(sum(gaps) / len(gaps), 1) if gaps else None,
        "min_gap_days": min(gaps) if gaps else None,
        "max_gap_days": max(gaps) if gaps else None,
        "release_count_last_year": release_count_last_year,
        "format_counts": format_counts,
        "timeline": parsed,
    }


def render_cadence_section(cadence: dict[str, Any]) -> None:
    if not cadence["timeline"] or cadence["avg_gap_days"] is None:
        st.info("발매 이력이 충분하지 않아 컴백 빈도를 분석할 수 없습니다.")
        return

    cols = st.columns(3)
    with cols[0]:
        st.markdown(
            f'<div class="glass-card"><div class="muted">평균 컴백 간격</div>'
            f'<div class="mono" style="font-size:1.8rem;font-weight:800;color:#fff;">'
            f'{cadence["avg_gap_days"]:.0f}일</div></div>',
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown(
            f'<div class="glass-card"><div class="muted">최근 1년 발매 횟수</div>'
            f'<div class="mono" style="font-size:1.8rem;font-weight:800;color:#fff;">'
            f'{cadence["release_count_last_year"]}회</div></div>',
            unsafe_allow_html=True,
        )
    with cols[2]:
        fastest = cadence["min_gap_days"]
        st.markdown(
            f'<div class="glass-card"><div class="muted">최단 컴백 간격</div>'
            f'<div class="mono" style="font-size:1.8rem;font-weight:800;color:#fff;">'
            f'{fastest if fastest is not None else "-"}일</div></div>',
            unsafe_allow_html=True,
        )

    timeline_df = pd.DataFrame(
        [{"발매일": dt.strftime("%Y-%m-%d"), "포맷": classify_format(a.get("track_count", 0)),
          "이름": a.get("name", "")} for dt, a in cadence["timeline"]]
    )
    fmt_fig = px.bar(
        pd.DataFrame(
            [{"포맷": k, "횟수": v} for k, v in cadence["format_counts"].items()]
        ),
        x="포맷", y="횟수", color="포맷",
        color_discrete_sequence=["#fa233b", "#fb5c74", "#ff9500", "#8c8c99"],
    )
    fmt_fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#d9dcec"), showlegend=False,
    )
    st.plotly_chart(fmt_fig, use_container_width=True, config={"displayModeBar": False})
    with st.expander("발매 타임라인 상세 보기"):
        st.dataframe(timeline_df, use_container_width=True, hide_index=True)


# =========================================================
# 11. NEW — 판매량/수익 예측 섹션
# =========================================================

def render_sales_prediction_section(
    artist_id: str,
    apple_data: dict[str, Any],
    youtube_data: list[dict[str, Any]],
    news_score_avg: float,
    components: dict[str, float],
) -> None:
    verified_records = get_sales_records(artist_id)
    chart_history = get_chart_history(artist_id)

    if verified_records:
        st.markdown(
            '<span class="verified-tag">✔ 실측 데이터 확보</span> '
            '<span class="muted">공개 보도자료(한터차트/서클차트) 기반 확정 수치</span>',
            unsafe_allow_html=True,
        )
        seed_df = pd.DataFrame([
            {
                "앨범": r["album_name"], "발매일": r["release_date"],
                "초동 판매량(장)": f'{r["first_week_sales"]:,}' if r["first_week_sales"] else "미확보",
                "기준": r["source_chart"], "비고": r["note"],
            }
            for r in verified_records
        ])
        st.dataframe(seed_df, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            '<span class="estimate-tag">◐ 신호 기반 추정</span> '
            '<span class="muted">아직 실측 확정 데이터가 없어, 아래는 스트리밍/유튜브/뉴스 신호로 만든 추정치입니다.</span>',
            unsafe_allow_html=True,
        )

    if chart_history:
        st.markdown(
            '<span class="verified-tag">✔ Spotify 글로벌 차트 실측</span> '
            '<span class="muted">Kaggle 공개 데이터셋(스포티파이 위클리 글로벌 앨범 차트) 기반</span>',
            unsafe_allow_html=True,
        )
        chart_df = pd.DataFrame([
            {
                "앨범": r["album_name"], "발매일": r["release_date"],
                "글로벌 최고 순위": r["best_global_rank"],
                "차트 체류 주수": r["max_weeks_on_chart"],
            }
            for r in chart_history
        ])
        st.dataframe(chart_df, use_container_width=True, hide_index=True)
        st.caption("⚠️ 이 데이터셋엔 한국(kr) 리전이 포함돼 있지 않아 글로벌 리전 기준입니다.")

    days_gap = days_since(apple_data.get("latest_album", {}).get("release_date"))
    signals = SignalInputs(
        apple_popularity_score=components.get("발매 최신성", 50),
        youtube_view_momentum=components.get("YouTube 반응", 50),
        news_buzz_score=news_score_avg,
        days_since_last_comeback=days_gap,
        album_format=classify_format(apple_data.get("latest_album", {}).get("total_tracks", 0)),
    )
    prediction = predict_first_week_sales(artist_id, signals)

    st.markdown("#### 📦 예상 초동 판매량 (물리 앨범)")
    cols = st.columns(3)
    labels = ["하한", "중앙값", "상한"]
    values = [prediction.low, prediction.mid, prediction.high]
    for col, label, value in zip(cols, labels, values):
        with col:
            st.markdown(
                f'<div class="revenue-band"><div class="val">{value:,}장</div>'
                f'<div class="lbl">{label}</div></div>',
                unsafe_allow_html=True,
            )
    confidence_map = {"high": "높음", "medium": "중간", "low": "낮음(초기 추정)"}
    st.caption(f"신뢰도: {confidence_map[prediction.confidence]} · {prediction.explanation}")

    st.markdown("#### 💰 예상 수익 (스트리밍 + 피지컬, 추정치)")
    revenue = estimate_revenue_band(prediction)
    r_cols = st.columns(3)
    for col, label, key in zip(r_cols, labels, ["low", "mid", "high"]):
        with col:
            st.markdown(
                f'<div class="revenue-band"><div class="val">'
                f'₩{revenue[key]["total_krw"]:,}</div><div class="lbl">{label}</div></div>',
                unsafe_allow_html=True,
            )
    st.caption(f"⚠️ {revenue['disclaimer']}")

    with st.expander("수익 계산 가정치 직접 조정해보기"):
        price = st.slider("앨범 평균 소비자가(원)", 10_000, 60_000, 25_000, step=1_000)
        margin = st.slider("기획사 순이익 비중", 0.1, 0.6, 0.35, step=0.05)
        streams_per_buyer = st.slider("구매자 1인당 평균 스트리밍 횟수", 0, 50, 15)
        per_stream = st.slider("스트리밍 1회당 정산액(원)", 1.0, 10.0, 4.0, step=0.5)
        custom_assumptions = RevenueAssumptions(
            avg_physical_album_price_krw=price,
            label_net_margin_ratio=margin,
            est_streams_per_physical_buyer=streams_per_buyer,
            revenue_per_stream_krw=per_stream,
        )
        custom_revenue = estimate_revenue_band(prediction, custom_assumptions)
        st.write(f"조정된 예상 수익(중앙값): **₩{custom_revenue['mid']['total_krw']:,}**")


# =========================================================
# 12. RENDER HELPERS
# =========================================================

def render_album_card(artist_name: str, apple_data: dict[str, Any]) -> None:
    album = apple_data.get("latest_album", {})
    image = album.get("image", "")
    apple_url = album.get("apple_url", "")
    img_tag = (
        f'<img src="{escape_text(image)}" class="album-cover" />'
        if image else '<div class="album-cover"></div>'
    )
    link_tag = (
        f'<a href="{escape_text(apple_url)}" target="_blank" '
        'style="color:#fb5c74;font-weight:700;">Apple Music에서 열기 ↗</a>'
        if apple_url else ""
    )
    st.markdown(
        f"""
        <div class="album-card">
            {img_tag}
            <div>
                <div class="muted">최신 발매작</div>
                <div class="album-name">{escape_text(album.get("name", "-"))}</div>
                <div class="muted">{escape_text(format_date(album.get("release_date")))} ·
                    {escape_text(album.get("album_type", ""))} ·
                    {escape_text(album.get("total_tracks", 0))}곡</div>
                <div style="margin-top:8px;">{link_tag}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_news_cards(news_items: list[dict[str, Any]]) -> None:
    if not news_items:
        st.info("표시할 뉴스가 없습니다.")
        return
    for item in news_items[:8]:
        title = escape_text(item.get("title", ""))
        url = escape_text(item.get("url", ""))
        source = escape_text(item.get("source", ""))
        date = escape_text(format_date(item.get("published_at")))
        title_html = f'<a href="{url}" target="_blank" class="news-title">{title}</a>' if url else f'<span class="news-title">{title}</span>'
        st.markdown(
            f'<div class="news-card">{title_html}<div class="news-meta">{source} · {date}</div></div>',
            unsafe_allow_html=True,
        )


def render_latest_mv(youtube_data: list[dict[str, Any]]) -> None:
    """최근 공식 유튜브 계정에서 공개한 뮤직비디오를 임베드."""
    if not youtube_data:
        st.info("표시할 유튜브 영상이 없습니다.")
        return
    latest = youtube_data[0]
    if latest.get("url"):
        st.video(latest["url"])
    st.markdown(
        f'<div class="muted" style="margin-top:8px;">{escape_text(latest.get("title",""))} · '
        f'{escape_text(latest.get("channel_title",""))} · '
        f'조회수 {format_number(latest.get("views",0))} · '
        f'{escape_text(format_date(latest.get("published_at")))}</div>',
        unsafe_allow_html=True,
    )
    if len(youtube_data) > 1:
        with st.expander("최근 다른 영상 더 보기"):
            for v in youtube_data[1:5]:
                st.markdown(
                    f'- [{escape_text(v.get("title",""))}]({escape_text(v.get("url",""))}) '
                    f'· 조회수 {format_number(v.get("views",0))}'
                )


# =========================================================
# 13. SIDEBAR — 그룹/솔로 선택
# =========================================================

st.sidebar.markdown("## 🎧 K-POP Comeback Radar")
st.sidebar.caption("그룹과 솔로를 분리해서 추적합니다.")

display_options = get_display_options()
option_keys = [k for k, _ in display_options]
option_labels = {k: label for k, label in display_options}

selected_key = st.sidebar.selectbox(
    "아티스트 선택",
    options=option_keys,
    format_func=lambda k: option_labels[k],
)

selected_entry = ARTISTS[selected_key]
selected_artist = selected_entry["display_name"]
is_solo = selected_entry["kind"] == "solo"

if is_solo:
    parent = ARTISTS.get(selected_entry.get("group_id") or "", {})
    st.sidebar.markdown(
        f'<span class="badge badge-solo">SOLO</span> '
        f'<span class="muted">소속: {escape_text(parent.get("display_name",""))}</span>',
        unsafe_allow_html=True,
    )
else:
    members = selected_entry.get("members", [])
    st.sidebar.markdown(
        f'<span class="badge">GROUP</span> <span class="muted">멤버: {len(members)}명</span>',
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 API 연결")

youtube_api_key = get_secret("YOUTUBE_API_KEY")
mediastack_api_key = get_secret("MEDIASTACK_API_KEY")
naver_client_id = get_secret("NAVER_CLIENT_ID")
naver_client_secret = get_secret("NAVER_CLIENT_SECRET")
solar_api_key = get_secret("UPSTAGE_API_KEY")
solar_model = get_secret("SOLAR_MODEL", "solar-pro")

youtube_connected = bool(youtube_api_key)
mediastack_connected = bool(mediastack_api_key)
naver_connected = bool(naver_client_id and naver_client_secret)
solar_connected = bool(solar_api_key)

demo_mode = st.sidebar.toggle("데모 모드 (API 없이 체험)", value=not (youtube_connected or mediastack_connected))

st.sidebar.write(f"{'🟢' if True else '⚪'} Apple Music (iTunes Search, 키 불필요)")
st.sidebar.write(f"{'🟢' if youtube_connected else '⚪'} YouTube Data API")
st.sidebar.write(f"{'🟢' if mediastack_connected else '⚪'} Mediastack (글로벌 뉴스)")
st.sidebar.write(f"{'🟢' if naver_connected else '⚪'} Naver News API")
st.sidebar.write(f"{'🟢' if solar_connected else '⚪'} Upstage Solar (AI 채팅)")


# =========================================================
# 14. DATA FETCH
# =========================================================

demo = get_demo_bundle(selected_artist)
apple_data = demo["apple"]
youtube_data = demo["youtube"]
global_news = demo["global_news"]
naver_news = demo["naver_news"]
active_sources: list[str] = []
api_errors: list[str] = []

try:
    apple_data = get_apple_music_data(selected_entry["apple_query"])
    active_sources.append("Apple Music Live")
except RuntimeError as error:
    api_errors.append(f"Apple: {error}")
    active_sources.append("Apple Demo")

if youtube_connected and not demo_mode:
    try:
        youtube_data = get_youtube_data(selected_entry["youtube_query"], youtube_api_key)
        active_sources.append("YouTube Live")
    except RuntimeError as error:
        api_errors.append(f"YouTube: {error}")
        active_sources.append("YouTube Demo")
else:
    active_sources.append("YouTube Demo")

if mediastack_connected and not demo_mode:
    try:
        global_news = get_global_news(selected_entry["global_news_query"], mediastack_api_key)
        active_sources.append("Mediastack Live")
    except RuntimeError as error:
        api_errors.append(f"Mediastack: {error}")
        active_sources.append("Global News Demo")
else:
    active_sources.append("Global News Demo")

if naver_connected and not demo_mode:
    try:
        naver_news = get_naver_news(selected_entry["naver_news_query"], naver_client_id, naver_client_secret)
        active_sources.append("Naver Live")
    except RuntimeError as error:
        api_errors.append(f"Naver: {error}")
        active_sources.append("Naver Demo")
else:
    active_sources.append("Naver Demo")


# =========================================================
# 15. SCORE + HERO
# =========================================================

score, components = calculate_comeback_score(apple_data, youtube_data, global_news, naver_news)
artist_data = apple_data.get("artist", {})

st.markdown(
    f"""
    <div class="hero">
        <div class="eyebrow">K-POP COMEBACK RADAR</div>
        <div class="hero-title">{escape_text(selected_entry["emoji"])} {escape_text(selected_artist)}
            {render_eq_bars(score)}
        </div>
        <div class="hero-subtitle">
            Apple Music·YouTube·글로벌/국내 뉴스 신호를 한 화면에서 추적하고,
            공개된 실측 판매 데이터 + 신호 기반 모델로 다음 컴백의 초동 판매량과
            수익을 추정합니다.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if api_errors:
    with st.expander("⚠️ 일부 데이터 소스 연결 실패 (데모로 대체됨)"):
        for err in api_errors:
            st.write(f"- {err}")

left, center, right = st.columns([1.05, 1.15, 0.9])

with left:
    st.markdown('<div class="section-title">🎵 Apple Music Profile</div>', unsafe_allow_html=True)
    st.write(f"장르: **{artist_data.get('genre','-')}**")
    st.write(f"카탈로그 앨범 수: **{artist_data.get('catalog_albums',0)}**")
    render_album_card(selected_artist, apple_data)

with center:
    st.markdown('<div class="section-title">🎬 최신 공식 뮤직비디오</div>', unsafe_allow_html=True)
    render_latest_mv(youtube_data)

with right:
    st.markdown('<div class="section-title">📈 Comeback Score</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="score-card">
            <div class="muted">현재 레이더 점수</div>
            <div class="score-number">{score:.0f}</div>
            <div style="font-size:1.02rem;font-weight:800;margin-top:8px;color:#fff;">
                {escape_text(score_label(score))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    radar_df = pd.DataFrame({"지표": list(components.keys()), "점수": list(components.values())})
    radar_fig = px.line_polar(radar_df, r="점수", theta="지표", line_close=True, range_r=[0, 100])
    radar_fig.update_traces(fill="toself", line=dict(color="#fb5c74"))
    radar_fig.update_layout(
        height=300, margin=dict(l=15, r=15, t=25, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(bgcolor="rgba(255,255,255,.03)",
                   radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,.10)"),
                   angularaxis=dict(gridcolor="rgba(255,255,255,.10)", tickfont=dict(size=10))),
        showlegend=False, font=dict(color="#d9dcec"),
    )
    st.plotly_chart(radar_fig, use_container_width=True, config={"displayModeBar": False})


# =========================================================
# 16. 컴백 빈도 분석
# =========================================================

st.markdown("---")
st.markdown('<div class="section-title">🗓️ 발매 빈도 분석 (싱글 포함)</div>', unsafe_allow_html=True)
cadence = analyze_release_cadence(apple_data.get("albums", []))
render_cadence_section(cadence)


# =========================================================
# 17. 판매량 / 수익 예측
# =========================================================

st.markdown("---")
st.markdown('<div class="section-title">💿 판매량 · 수익 예측</div>', unsafe_allow_html=True)
news_avg = (components.get("글로벌 뉴스", 0) + components.get("국내 뉴스", 0)) / 2
render_sales_prediction_section(selected_key, apple_data, youtube_data, news_avg, components)


# =========================================================
# 18. 뉴스
# =========================================================

st.markdown("---")
st.markdown('<div class="section-title">📰 Comeback News Monitor</div>', unsafe_allow_html=True)
global_tab, korean_tab = st.tabs(["🌎 Global News", "🇰🇷 Korean News"])
with global_tab:
    st.caption("Mediastack을 통해 수집한 영문권 기사입니다.")
    render_news_cards(global_news)
with korean_tab:
    st.caption("네이버 검색 API를 통해 수집한 국내 최신 기사입니다.")
    render_news_cards(naver_news)


# =========================================================
# 19. FOOTER
# =========================================================

st.markdown("---")
st.caption(
    "K-POP Comeback Radar v2 · Apple iTunes Search API · YouTube Data API · "
    "Mediastack · Naver Search API · Upstage Solar · "
    "판매량/수익 예측은 공개 보도자료 기반 실측치 + 신호 기반 추정 모델의 결과이며, "
    "실제 정산과 다를 수 있는 비공식 학습용 지표입니다."
)
