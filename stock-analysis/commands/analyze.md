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
  - Task
  - TodoWrite
---

# Stock Analysis Command

Conduct comprehensive stock analysis following the research-first workflow.

## Arguments

- `ticker` (required): Stock ticker symbol (e.g., AAPL, MSFT, OWL)
- `output-path` (optional): Directory path to save the analysis document

## Workflow

### Phase 1: Free-Form Research

Use WebSearch and WebFetch to investigate:

1. **Company Overview**
   - Search: "{Company} business model revenue segments"
   - Understand what the company does and how it makes money

2. **Recent Developments**
   - Search: "{Ticker} earnings Q4 2024 guidance outlook"
   - Search: "{Company} news announcements {current month} {year}"

3. **Financial Data**
   - Search: "{Ticker} stock price market cap valuation 2025"
   - Search: "{Company} financial statements revenue earnings"

4. **Ownership & Sentiment**
   - Search: "{Ticker} insider buying selling transactions"
   - Search: "{Ticker} analyst ratings price target"

5. **Industry Context**
   - Search: "{Company} competitors comparison market share"
   - Search: "{Sector} industry outlook risks 2025"

### Phase 2: Sector-Specific Metrics

Load the `sector-metrics-guide` skill to identify relevant industry metrics.

Based on the company's sector, gather:
- Industry-specific KPIs
- GAAP vs Non-GAAP differences
- Benchmark comparisons

### Phase 3: Competitive Analysis

Research main competitors:
- Market positioning
- Relative valuation
- Competitive advantages/disadvantages

### Phase 4: Risk Assessment

Identify and document:
- Business model risks
- Financial risks (debt, dilution)
- Regulatory risks
- Management risks
- Macro risks

### Phase 5: CEO Evaluation

Research leadership:
- Background and track record
- Insider ownership
- Recent insider transactions
- Compensation alignment

### Phase 6: Valuation & Fair Price Estimation

기업 유형에 맞는 밸류에이션 방법론을 2~3개 교차 적용하여 적정가 범위를 산출.

**방법론 참고**: Vault 내 `밸류에이션 적정가 산출 방법론` 문서가 있으면 Read하여 참고.

**기업 유형별 추천 조합**:

| 기업 유형 | 1차 | 2차 | 3차/보조 |
|----------|-----|-----|---------|
| 흑자 성숙기업 | DCF | P/E Comp | Backward DCF |
| 적자 고성장기업 | EV/Sales Comp | PSG | Backward DCF |
| 프리레버뉴 기업 | rNPV (확률가중) | Comp (유사기업) | EV/Cash + Backward DCF |
| 금융/리츠 | P/B 또는 NAV | DDM | P/E Comp |

**산출 절차**:
1. 기업 유형 판별 → 적합한 방법론 2~3개 선택
2. 각 방법론별 적정가 산출 (계산 과정 명시)
3. 종합 적정가 범위 제시 (현재가 대비 상승/하락 여력)
4. 핵심 변수 민감도 분석 (할인율, 성장률, 확률 변동 시 적정가 변화)

**rNPV 적용 시** (프리레버뉴/바이오 등):
- 최소 3개 시나리오(강세/기본/약세) 정의
- 각 시나리오에 확률, 목표연도 매출, EV/배수 부여
- 할인율 적용하여 현재가치 산출 후 확률 가중 합산

**출력 형식**:
```markdown
### 적정가 산출 (YYYY-MM-DD 기준)
#### 1차: [방법론명] — 핵심 산출
[계산 과정]
#### 2차: [방법론명]
[계산 과정]
#### 적정가 종합
| 방법론 | 적정가 | 현재가 대비 |
```

## Output

After completing research, create the analysis document:

1. If `output-path` provided: Save to `{output-path}/{ticker} 종목분석.md`
2. If no path: Ask user where to save or display summary

Use the template from `stock-analysis-workflow` skill's `references/analysis-template.md`.

## Example Usage

```
/stock-analysis:analyze AAPL
/stock-analysis:analyze NVDA D:\Documents\StockAnalysis
/stock-analysis:analyze OWL ./analysis
```

## Tips

- For thorough research, use the `stock-researcher` agent
- Cross-reference multiple sources for key data points
- Note data freshness - earnings data may be from previous quarter
- Document sources for important claims
