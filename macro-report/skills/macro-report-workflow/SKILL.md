---
name: Macro Report Workflow
description: This skill should be used when the user asks to "generate macro report", "analyze market conditions", "create investment report", "run macro analysis", "거시경제 분석", "시장 환경 분석", "종합 투자 분석", "유동성 분석", "내부자 매매 분석", "크로스에셋 분석", "백테스트 갱신", "추천 이력 업데이트", "backtest update"
version: 1.2.0
---

# 거시경제 종합 투자분석 워크플로우

## 개요

5개 개별 분석 보고서를 수집·작성하고, 종합 투자판단 보고서를 생성하는 워크플로우.

## 핵심 원칙: "Scan First, Baseline Second"

1. **열린 스캔**: 최근 2주간 핵심 이벤트를 먼저 파악하여 새로운 것을 놓치지 않음
2. **베이스라인 활용**: 이전 보고서를 기준으로 변경분만 업데이트하여 토큰 절약
3. **조사-작성 분리**: Sonnet(수집) → Opus(분석) 분리로 비용 최적화

## 3단계 파이프라인

```
[1단계] macro-scanner (Sonnet) × 5 병렬
  ├── 질문 템플릿 직접 Read (경로만 수신)
  ├── 열린 스캔: 새 이벤트 발견
  ├── 베이스라인: 이전 보고서 대비 변경분 식별
  ├── 데이터 수집: 항목별 최신 수치
  └── 수집 결과를 .scan/ 파일로 Write (오케스트레이터에 전문 미반환)

[2단계] macro-writer (Opus) × 5 병렬
  ├── .scan/ 파일에서 수집 데이터 Read
  ├── 개별 보고서 작성·저장
  └── 종합보고서용 요약 섹션 (20~30줄) 추가

[3단계] macro-writer (Opus) × 1
  ├── 5개 보고서의 요약 섹션 먼저 Read (~150줄) → 전체 구조 파악
  ├── 5개 보고서 전문을 순차적 Read → 상세 데이터 수집
  └── 종합보고서 작성
```

### 토큰 최적화 설계

1. **파일 기반 핸드오프**: Scanner 결과를 오케스트레이터에 반환하지 않고 파일로 전달하여 동일 데이터 3회 처리 제거
2. **경로 참조**: 질문 템플릿·스코어링 기준 등 참조 문서를 오케스트레이터가 로드하지 않고 에이전트가 직접 Read
3. **요약 우선 읽기**: 종합 Writer가 요약(~150줄)으로 구조를 먼저 파악한 뒤 전문을 순차 Read

## 5개 보고서 구성

| 보고서 | 핵심 질문 | 질문 항목 수 |
|--------|---------|------------|
| 내부자 매매 동향 | CEO/CFO가 자사주를 사고 있는가? | 13개 |
| 애널리스트 목표가 변동 | 월스트리트가 어디에 베팅하는가? | 15개 |
| 시장 주도 업종 분석 | 스마트머니가 어디로 이동하는가? | 12개 |
| 유동성 환경 분석 | 시장에 돈이 풀리고 있는가? | 19개 |
| 크로스에셋 레짐 분석 | 지금은 어떤 장인가? | 10개 |

## 종합보고서 구조

5개 보고서를 교차 분석하여 투자 판단을 내리는 **메타 보고서**:

1. 현재 시장 환경 평가 (5개 요약)
2. **교차 시그널 심층 분석** (신호 반전·괴리, 스마트머니 vs 리테일, 옵션 포지셔닝)
3. 투자 적합성 판단 (0~100점)
4. 추천 투자 종목 (Tier 1~4 + 공급망 수혜주)
5. 지역 로테이션 전략
6. 포트폴리오 전략 (배분 트리맵)
7. 타이밍 및 실행 계획 (3개월 로드맵)
8. 리스크 관리 (경고 임계점 + 신규 시스템 리스크)
9. 최종 결론

## 커맨드

| 커맨드 | 용도 |
|--------|------|
| `/macro-report:generate` | 전체 워크플로우 (5개 + 종합) |
| `/macro-report:report [type]` | 개별 보고서 1개 |
| `/macro-report:synthesize [date]` | 종합보고서만 (기존 5개 활용) |

## 질문 템플릿

각 보고서의 질문 항목은 `references/question-*.md`에 정의되어 있으며, macro-scanner에게 전달되어 데이터 수집 가이드로 활용된다.

## 데이터 수집 경로

macro-scanner 는 두 가지 경로를 지원한다 (자세한 흐름은 `agents/macro-scanner.md`):

- **신규 경로 (default, B 모드)**: `https://stock.xhhan.com/api/meta/capabilities` 를 먼저 fetch 해 사용 가능한 데이터/엔드포인트를 동적으로 파악한 뒤, 매칭되는 항목은 financial-data-platform API 로, 못 하는 항목만 WebSearch fallback. **사전 매핑 금지** — 매핑은 매 실행마다 capabilities 응답이 결정한다.
- **기존 경로 (A 모드)**: 전통적인 WebSearch-only. `--no-api` 인자 또는 `MACRO_SKIP_API=1` 환경변수로 강제.

토큰 절감 효과 측정 양식은 [token-savings.md](references/token-savings.md) 참고.

## 출력

- Obsidian 호환 마크다운
- Plotly 차트 포함
- `[[]]` 위키링크
- 한국어 기반
