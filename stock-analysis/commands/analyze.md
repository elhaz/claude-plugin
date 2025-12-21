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
