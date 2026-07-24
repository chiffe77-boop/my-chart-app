# 🎧 K-POP Comeback Radar

Apple Music · YouTube · 국내외 뉴스 신호를 한 화면에서 추적하고,
컴백 앨범의 **예상 초동 판매량**과 **수익**까지 추정하는 K-POP 컴백 분석 대시보드.

---

## ✨ 주요 기능

| 기능 | 설명 |
|---|---|
| 🎵 Apple Music 프로필 | iTunes Search API로 최신 앨범·트랙 실시간 조회 |
| 🧑‍🤝‍🧑 그룹 / 솔로 분리 | 41개 아티스트 — 그룹 선택 시 소속 솔로 멤버도 바로 조회 |
| 🎬 최신 뮤직비디오 | 공식 유튜브 채널의 최신 영상을 화면에 바로 임베드 |
| 📈 Comeback Score | 발매 시점·유튜브 반응·뉴스 버즈를 가중 합산한 레이더 지표 |
| 🗓️ 발매 빈도 분석 | 싱글 포함 컴백 간격, 최근 1년 발매 횟수, 포맷별 분포 |
| 💿 판매량 · 수익 예측 | 실측 데이터 + 신호 기반 모델로 초동 판매량·수익 구간 추정 |
| 🤖 AI 채팅 분석 | Upstage Solar 기반 컴백 데이터 Q&A |

---

## 📁 파일 구조

```
kpop_radar/
├── main.py               # 메인 앱 (실행 진입점)
├── artists_data.py       # 아티스트 데이터베이스 (그룹 23 + 솔로 18)
├── seed_sales.py         # 실측 판매량 시드 데이터
├── prediction_model.py   # 판매량·수익 예측 모델
└── requirements.txt
```

> `main.py`만 실행하면 되지만, 나머지 3개 `.py` 파일이 **같은 폴더**에 있어야 합니다.

---

## 🚀 실행 방법

```bash
pip install -r requirements.txt
streamlit run main.py
```

API 키가 없어도 **데모 모드**로 바로 체험 가능합니다.

---

## 🔑 API 키 (선택 사항)

`.streamlit/secrets.toml`에 등록하거나, Streamlit Cloud라면 **Settings → Secrets**에 추가하세요.

```toml
YOUTUBE_API_KEY = "..."
MEDIASTACK_API_KEY = "..."
NAVER_CLIENT_ID = "..."
NAVER_CLIENT_SECRET = "..."
UPSTAGE_API_KEY = "..."
```

키가 없어도 Apple Music 데이터는 인증 없이 바로 조회됩니다.

---

## 📊 판매량/수익 예측 — 어떻게 작동하나

```
seed_sales.py (공개 보도자료 기반 실측 초동 판매량)
        │
        ├─▶ 실측 있으면 화면에 "✔ 실측 데이터" 표로 표시
        │
        └─▶ prediction_model.py 기준선(baseline)에 반영
                    │
                    └─▶ 이번 컴백의 신호(스트리밍·유튜브·뉴스)와 곱해
                        "예상 초동 판매량 + 수익" 구간 산출
```

⚠️ 수익 추정치는 업계 공개 벤치마치를 적용한 **일러스트레이션**이며,
실제 기획사 정산과 다를 수 있습니다. 가정치는 화면에서 슬라이더로 직접 조정 가능합니다.

---

## 🛠️ 기술 스택

`Streamlit` · `Plotly` · `Pandas` · `Apple iTunes Search API` · `YouTube Data API` ·
`Mediastack` · `Naver Search API` · `Upstage Solar`

---

## 📌 로드맵

- [ ] 시드 판매 데이터 추가 확보 (ATEEZ, TXT, ENHYPEN, 솔로 앨범 등)
- [ ] `seed_sales.py` → `prediction_model.py` 기준선 자동 동기화
- [ ] 실측 레코드 30개 이상 확보 시 회귀 기반 예측 모델로 업그레이드

---

<sub>비공식 팬 프로젝트 · 학습/포트폴리오 목적 · Comeback Score 및 판매 예측은 공식 지표가 아닙니다.</sub>
