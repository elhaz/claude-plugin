---
name: Macro Report Workflow
description: This skill should be used when the user asks to "generate macro report", "weekly macro report", "run macro analysis", "거시경제 분석", "거시경제 주간 보고", "시장 전망", "1·3·6개월 전망", "예측 채점", "지난 예측 성적", "판단 파일", "뉴스 헤드라인 수집", "쉬운말 보고서", "시장 환경 분석", "유동성 분석", "크로스에셋 분석"
version: 2.1.1
---

# 거시경제 주간 보고 워크플로우 (v2)

## 개요

한 주치 세계 뉴스와 시장 데이터로 **1·3·6개월 뒤를 예측**하고, 그 예측을 **채점 가능한 원장**으로 남기며, 사람은 **쉬운말 주간 보고 하나**만 읽는다.

v1(1.7.0, 2025-10 ~ 2026-09-28)은 지난 데이터 요약 → 개별 종목 추천이었고, 백테스트 결과 S&P 500 대비 승률이 약 50%(동전던지기)였다. 사용자는 쉬운말 보고서만 읽는데 토큰은 대부분 사람이 읽지 않는 전문판·개별 보고서·차트에 쓰였다. v2 는 이 두 문제를 고친다. 설계 근거는 Vault `01_Projects/사이드프로젝트/거시경제 보고서 v2 설계.md`.

## 파이프라인

```
[1부] /macro-report:collect
  ├── fetch_headlines.py — 데이터 플랫폼이 3시간마다 누적한 RSS 헤드라인 → 거시 관련 필터
  └── macro-scanner (Sonnet) × 5 병렬: liquidity · regime · sector · insider · outlook
        └── 데이터/{날짜}/{type}.md  (숫자·사실·출처만, 영구 보관)

[2부] /macro-report:weekly
  └── macro-writer (inherit — 세션 모델) × 1
        ├── 데이터 파일 5개 + 지난주 판단 → 판단.md (예측 원장 JSON)
        ├── weekly_score.py validate → score (만기 예측 채점 + 차트 2개 → 채점.md)
        └── {날짜} 거시경제 주간 보고.md (쉬운말, 공개 게시 대상)
```

## 예측과 채점

| 대상 | 형태 | 채점 |
|---|---|---|
| 업종·지역 ETF 20개 | 1·3·6개월 뒤 S&P 500 보다 잘할 **확률** | Brier 점수 (기준 0.25) |
| 비중안 (자산군 4 + ETF 20 중) | 합계 100 | 그대로 보유 시 수익 vs 60/40 |
| 거시 변수 11개 | 방향 (up/down/flat) | 방향 적중 — 진단용 |

- 실제값은 financial-data-platform API (FRED·가격). 개별 종목 추천은 하지 않는다
- 시장 내재 기대치(FedWatch, `/api/fed-expectations/latest`)와 **다르게 본 부분**이 v2 의 핵심 가치
- 형식: [judgment-schema.md](references/judgment-schema.md)

## 뉴스 출처 (약관 확인)

연합뉴스(경제·마켓·국제)·CNBC·연준 RSS 를 데이터 플랫폼이 누적 → 내부망 전용 API → `fetch_headlines.py`. 여기에 FOMC 일정, FedWatch, WebSearch. MarketWatch·Google News·SAVE·FinancialJuice 는 약관상 자동 수집 금지라 쓰지 않는다. **기사 문장을 옮기지 않고**, 사실은 자체 문장으로, 근거는 각주 원문 링크로. 상세: [question-outlook.md](references/question-outlook.md)

## 참고 문서

| 문서 | 단일 출처 범위 |
|---|---|
| [judgment-schema.md](references/judgment-schema.md) | 판단 파일·JSON 스키마·예측 대상·확률 쓰는 법 |
| [weekly-report-template.md](references/weekly-report-template.md) | 주간 보고 구조·각주·줄바꿈·차트 |
| [plain-language-guide.md](references/plain-language-guide.md) | 문체·용어 사전·교차 정합성 |
| [scoring-criteria.md](references/scoring-criteria.md) | 시장 점수 (v2 가중치) · 내부자 등급 |
| `question-{liquidity,regime,sector,insider,outlook}.md` | scanner 수집 항목 |
| [data-gaps-conventions.md](references/data-gaps-conventions.md) | 데이터 갭 명명 |

## 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/macro-report:collect [날짜]` | 1부 — 헤드라인 + 데이터 파일 5종 |
| `/macro-report:weekly [날짜]` | 2부 — 판단 + 채점 + 주간 보고 |

한 세션에서 1부·2부를 연달아 돌리면 5시간 한도에 걸릴 수 있어 루틴은 둘로 나눠 돈다 (Vault 밖 `~/.claude/commands/주간거시보고.md`).

## 출력

- Obsidian 호환 마크다운, `[[]]` 위키링크, 한국어
- Plotly 차트는 주간 보고에 2개 (채점 스크립트 생성)
