---
name: analyze
description: Start comprehensive stock analysis for a given ticker
argument-hint: "[ticker] [output-path]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
---

# Stock Analysis Command

2-Agent 파이프라인으로 종목분석 문서를 생성한다.

## Arguments

- `ticker` (required): Stock ticker symbol (e.g., AAPL, MSFT, 051910)
- `output-path` (optional): Path to save the analysis document

## Workflow

### Step 1: Data Collection (stock-data-collector, Sonnet)

`stock-data-collector` 에이전트를 호출하여 정량 데이터를 수집한다.

**에이전트 프롬프트에 반드시 포함할 내용**:
- 티커: {ticker}
- 시장 가이드 참조 지시 (티커 형식에 따라 us/kr)
- 필수 수집 항목 전체 나열 (밸류에이션 11개, 분기별 재무, 연도별 추이, Peer 비교, 수급)

**에이전트 반환**: 구조화된 데이터 (테이블 형태)

### Step 2: Analysis & Document (stock-analyst, Opus)

`stock-analyst` 에이전트를 호출하여 분석 + 문서 작성한다.

**에이전트 프롬프트에 반드시 포함할 내용**:
- Step 1에서 수집된 데이터 전체 (복사하여 전달)
- 출력 파일 경로: {output-path}
- 시장 가이드 참조 지시
- 필수 산출물: 경쟁 분석, 어닝콜 Q&A, SWOT, 적정가, Plotly 차트

**에이전트 산출물**: 완성된 종목분석 .md 파일

## 오케스트레이션 예시

```
1. stock-data-collector 호출:
   "Collect all quantitative data for {TICKER}.
    Read references/us-market-guide.md (or kr-market-guide.md).
    Return structured data including: valuation set (11 metrics),
    quarterly financials (5Q), valuation history (3-5Y),
    peer comparison (2-3 companies), analyst/insider/short interest."

2. 반환된 데이터 확인 (누락 체크)

3. stock-analyst 호출:
   "Based on the following collected data for {TICKER}:
    [Step 1 데이터 전체 붙여넣기]

    Write complete analysis to {output-path}.
    Include: competitive analysis, earnings call Q&A,
    SWOT, fair value estimation, Plotly charts (3+).
    Read references/chart-templates.md for chart format."
```

## Example Usage

```
/stock-analysis:analyze AAPL
/stock-analysis:analyze NVDA 03_Resources/주식분석/종목분석/엔비디아.md
/stock-analysis:analyze 051910 03_Resources/주식분석/종목분석/LG화학.md
```
