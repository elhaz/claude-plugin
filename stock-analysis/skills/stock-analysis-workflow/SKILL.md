---
name: Stock Analysis Workflow
description: This skill should be used when the user asks to "analyze a stock", "research a company", "investigate a ticker", "do stock analysis", "evaluate an investment", "study a company's fundamentals", or mentions stock research, equity analysis, or investment research. Provides a systematic workflow for comprehensive stock analysis.
version: 1.0.0
---

# Stock Analysis Workflow

## Overview

A systematic approach to stock analysis that prioritizes discovery over template-filling. Start with free-form research to understand the business, then use templates to ensure completeness.

## Core Principle

**Research First, Template Second**

Templates designed for universal coverage may miss industry-specific insights. Free-form investigation reveals what makes each company unique before standardizing the output.

## Workflow Steps

### Step 1: Free-Form Research

Begin with open-ended investigation covering:

1. **Business Model Understanding**
   - What does the company actually do?
   - How does it make money?
   - Who are the customers?

2. **Recent Developments**
   - Latest earnings and guidance
   - Management changes
   - Strategic announcements
   - M&A activity

3. **Industry Context**
   - Sector sentiment (bullish/bearish/neutral)
   - Recent industry events (bankruptcies, regulations, disruptions)
   - Competitive positioning

4. **Unique Characteristics**
   - What differentiates this company?
   - Industry-specific metrics that matter
   - GAAP vs Non-GAAP considerations

### Step 2: Data Collection

Gather quantitative data systematically:

**Company Fundamentals:**
- Current price, market cap, 52-week range
- Valuation metrics (P/E, P/S, PEG, EV/EBITDA)
- Growth rates (revenue, earnings, margins)
- Balance sheet health (debt ratio, current ratio)

**Ownership & Sentiment:**
- Insider transactions (especially cluster buying)
- Institutional ownership changes
- Short interest
- Analyst ratings and price targets

**Industry-Specific Metrics:**
- Consult `sector-metrics-guide` skill for relevant metrics
- Identify GAAP vs Non-GAAP differences
- Note industry benchmarks

### Step 3: Template Application

Apply the analysis template to ensure completeness:

문서 구조(절 순서·frontmatter)의 단일 출처는 `stock-analyst` 에이전트 정의다. `references/analysis-template.md` 는 절별 작성 예시로 참고한다.

### Step 4: Valuation & Fair Price Estimation

기업 유형에 맞는 밸류에이션 방법론 2~3개를 교차 적용하여 적정가 범위 산출:

기업 유형별 방법론 표는 `stock-analyst` 에이전트 정의(Phase 3)를 따른다.

**산출 원칙**:
- 단일 방법론에 의존하지 말 것 — 최소 2개 교차 적용
- 계산 과정을 명시하여 추후 업데이트 시 재산출 용이하게
- 핵심 변수 민감도 분석 포함 (할인율, 성장률, 확률 변동)
- Vault 내 `밸류에이션 적정가 산출 방법론` 문서가 있으면 참조

### Step 5: Synthesis & Judgment

Form investment conclusions:

1. **Bull Case** - What needs to go right?
2. **Bear Case** - What could go wrong?
3. **Catalyst Timeline** - When might value be realized?
4. **Position Sizing** - Risk/reward assessment

## Information Often Missed

When following templates blindly, these insights are frequently overlooked:

| Category | Examples |
|----------|----------|
| **Industry Metrics** | FRE margin (asset managers), FFO (REITs), ARR (SaaS) |
| **Structural Issues** | Share dilution rate, GAAP vs Non-GAAP gaps |
| **Context** | Why is the sector weak/strong right now? |
| **Management Quality** | Co-CEO structures, founder involvement |
| **Timing** | Why is now the right entry point? |

## Web Research Strategy

When conducting web research for a stock:

**Search Queries to Use:**
```
"{Company} business model revenue segments"
"{Ticker} earnings {최근 분기} guidance"
"{Company} insider buying selling {month} {year}"
"{Company} vs {Competitor} comparison"
"{Company} risks concerns {year}"
"{Ticker} analyst ratings price target"
```

**Key Sources:**
- Company IR page for official filings
- SEC EDGAR for insider transactions
- Financial news for recent developments
- Industry publications for sector context

## Output Format

Generate analysis documents with:

1. **YAML Frontmatter**
   - tags, ticker, sector, created, updated

2. **Standard Sections**
   - Current status
   - Investment thesis
   - Financials
   - Business model
   - Risks
   - Action items

3. **Industry-Specific Additions**
   - Relevant sector metrics
   - GAAP vs Non-GAAP notes
   - Competitive comparison

## 자동 실행

`/stock-analysis:analyze {TICKER}` 가 `stock-data-collector`(수집) → `stock-analyst`(분석·문서) 순으로 에이전트를 호출한다. 기존 문서 갱신은 `/stock-analysis:update`.

## Additional Resources

### Reference Files

- **`references/analysis-template.md`** - Complete analysis document template
- **`references/research-checklist.md`** - Pre-analysis checklist

### Related Skills

- **`sector-metrics-guide`** - Industry-specific metrics and benchmarks

## Quick Reference

| Phase | Focus | Output |
|-------|-------|--------|
| 1. Research | Understanding | Business insights, unique factors |
| 2. Data | Quantification | Metrics, comparables, ownership |
| 3. Template | Completeness | Structured document |
| 4. Synthesis | Judgment | Investment decision |

Remember: The goal is informed judgment, not completed forms. A shorter analysis with genuine insight beats a lengthy template with no conviction.
