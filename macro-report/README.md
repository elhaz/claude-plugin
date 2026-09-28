# macro-report

거시경제 주간 보고 자동화 플러그인 (v2)

## 개요

한 주치 세계 뉴스와 시장 데이터로 **1·3·6개월 뒤를 예측**하고, 예측을 **채점 가능한 원장**으로 남긴 뒤, 사람이 읽을 **쉬운말 주간 보고** 한 개를 만듭니다.

- 예측 대상: 업종·지역 ETF 20개의 S&P 500 대비 확률, 비중안(자산군 + ETF), 거시 변수 11개 방향
- 채점: 매주 만기가 된 예측을 financial-data-platform 의 실제값으로 채점 (Brier 점수, 60/40 대비 초과수익, 방향 적중)
- 개별 종목 추천은 하지 않습니다 (v1 백테스트에서 S&P 500 대비 승률 약 50%)

## 아키텍처

```
[1부] /macro-report:collect
  ├── scripts/fetch_headlines.py   — 누적된 RSS 헤드라인 → 거시 관련 필터 (내부망 API)
  └── macro-scanner (Sonnet) × 5   — liquidity · regime · sector · insider · outlook
        → 분석/데이터/{날짜}/{type}.md

[2부] /macro-report:weekly
  └── macro-writer (Opus) × 1
        ├── 판단.md (예측 원장 ```json)
        ├── scripts/weekly_score.py validate / score → 채점.md (성적표 + 차트 2개)
        └── {날짜} 거시경제 주간 보고.md
```

## 커맨드

| 커맨드 | 용도 | 사용법 |
|--------|------|--------|
| `collect` | 1부: 헤드라인 + 데이터 파일 5종 | `/macro-report:collect [YYYY-MM-DD] [--no-api] [--api-base=URL]` |
| `weekly` | 2부: 판단 + 채점 + 주간 보고 | `/macro-report:weekly [YYYY-MM-DD] [--api-base=URL]` |

## 에이전트

| 에이전트 | 모델 | 역할 |
|----------|------|------|
| `macro-scanner` | Sonnet | 데이터 수집 (판단 없음), 유형별 데이터 파일 |
| `macro-writer` | Opus (inherit) | 판단 파일 → 검증·채점 → 주간 보고 |

## 스크립트 (표준 라이브러리만)

| 스크립트 | 용도 |
|---|---|
| `scripts/fetch_headlines.py` | `/api/news/headlines` (내부망 전용) → 거시 키워드 필터 → `데이터/{날짜}/뉴스헤드라인.md` |
| `scripts/weekly_score.py validate <판단.md>` | 판단 파일 스키마 검증 |
| `scripts/weekly_score.py score --data-root <데이터> --date <날짜>` | 모든 판단 파일의 만기 예측 채점 + 차트 → `채점.md` |

## 환경 / 의존

| 항목 | 용도 |
|---|---|
| `OBSIDIAN_VAULT` | Vault 루트. 출력: `$OBSIDIAN_VAULT/02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/` |
| financial-data-platform ≥ v0.6.0 | 가격·FRED·FedWatch(`/api/fed-expectations/*`)·뉴스 헤드라인(`/api/news/headlines`, 내부망 전용) |
| `FDP_API_BASE` | 채점·scanner 가 쓰는 데이터 플랫폼 주소 (채점 기본: `http://localhost:8000` → `https://stock.xhhan.com`) |
| `FDP_INTERNAL_BASE` | 헤드라인 조회용 내부망 주소 (기본 `http://localhost:8000`) |
| `FDP_API_KEY` | (선택) scanner 데이터 갭을 `POST /api/meta/data-gaps` 로 전송 |
| `--no-api` / `MACRO_SKIP_API=1` | scanner 를 WebSearch-only 로 |

## 출력 파일

| 파일 | 대상 |
|---|---|
| `분석/데이터/{날짜}/{liquidity,regime,sector,insider,outlook}.md` | LLM 입력 (영구 보관, 게시 안 함) |
| `분석/데이터/{날짜}/뉴스헤드라인.md` | LLM 입력 — 연합뉴스 RSS 는 개인 용도만 허용, **게시 금지** |
| `분석/데이터/{날짜}/판단.md` | 예측 원장 — 게시 후 수정 금지 |
| `분석/데이터/{날짜}/채점.md` | 성적표 + 차트 |
| `분석/{날짜} 거시경제 주간 보고.md` | 사람이 읽는 유일한 문서 (공개 게시) |

## Version History

- **2.0.0** (2026-09-28): 전면 개편 — 과거 데이터 요약 + 종목 추천(v1)을 **뉴스 기반 1·3·6개월 예측 + 채점**으로 교체. 개별 보고서 5종·종합·쉬운말 6종 → 데이터 파일 5종 + 판단 파일 + 주간 보고 1개. 애널리스트 목표가 보고서 제거, 뉴스·전망(`outlook`) 신설. 판단 파일 JSON 을 예측 원장으로 쓰고 `weekly_score.py` 가 매주 채점. 커맨드 `generate`/`report`/`synthesize`/`plain`/`backtest` 를 `collect`/`weekly` 로 교체 (v1 은 태그 `macro-report-v1.7.0`).
- **1.7.0** (2026-09-20): `OBSIDIAN_VAULT` 환경변수 지원.
- **1.6.0** (2026-07-27): 쉬운말 버전(평이판) 생성 기능 추가.
- **1.5.1** (2026-04-27): data_gaps POST 의 Windows cp949 결함 수정 ([#5](https://github.com/elhaz/claude-plugin/issues/5)).
- **1.5.0** (2026-04-27): data_gaps 짝꿍 활성화.
- **1.4.0** (2026-04-26): financial-data-platform capabilities 우선 경로 시범 도입.
- **1.3.0** (2026-04-25): 토큰 최적화 — 파일 기반 핸드오프, 경로 참조, 요약 우선 읽기.
- **1.0.0** (2026-03-29): 초기 릴리즈.
