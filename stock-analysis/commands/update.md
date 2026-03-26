---
name: update
description: Update existing stock analysis with recent developments
argument-hint: "[ticker] [existing-file-path]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
---

# Stock Analysis Update Command

기존 종목분석 문서를 2-Agent 파이프라인으로 갱신한다.

## Arguments

- `ticker` (required): Stock ticker symbol
- `existing-file-path` (required): Path to the existing analysis document

## Workflow

### Step 0: Load Existing Document

1. 기존 문서를 Read하여 메타데이터 파악
   - `updated` 필드에서 마지막 분석 일자 확인
   - 기존 적정가, 핵심 지표 기록
2. 시장 감지 (티커 형식)

### Step 1: Delta Data Collection (stock-data-collector, Sonnet)

`stock-data-collector` 에이전트를 호출하되, **마지막 분석일 이후 변경분**에 초점.

**에이전트 프롬프트에 포함**:
- 티커 + 마지막 분석일
- "이 날짜 이후의 변경사항 중심으로 수집"
- 현재 가격/밸류에이션 세트 갱신
- 새 분기 실적 발표 여부
- 애널리스트 목표가 변동
- 내부자/수급 변동

### Step 2: Analysis & Update (stock-analyst, Opus)

`stock-analyst` 에이전트를 호출하여 기존 문서를 갱신.

**에이전트 프롬프트에 포함**:
- 기존 문서 내용 (Read한 전문)
- Step 1에서 수집된 델타 데이터
- 갱신 지시:
  - frontmatter `updated` 날짜 갱신
  - 밸류에이션 지표 갱신
  - 새 분기 데이터 추가 (테이블 + 차트)
  - SWOT 갱신 (신규 이벤트 반영)
  - 적정가 재산출 트리거 체크 (주가 15%+ 변동, 신규 실적)
  - 업데이트 이력 추가

### 적정가 재산출 트리거

아래 중 하나라도 해당 시 적정가 재산출:
- 주가 15%+ 변동
- 새 실적 발표 (매출/이익 변동)
- 중대 뉴스 (M&A, CEO 교체, 규제 등)
- 희석 이벤트 (유상증자, 전환사채 등)

### 업데이트 이력 형식

```markdown
## 업데이트 이력

### [YYYY-MM-DD] 업데이트
- **가격 변동**: $XX → $YY (±Z%)
- **주요 변경**: [핵심 변경사항]
- **투자의견 변화**: [유지/상향/하향]
```

## Example Usage

```
/stock-analysis:update AAPL 03_Resources/주식분석/종목분석/애플.md
/stock-analysis:update 051910 03_Resources/주식분석/종목분석/LG화학.md
```
