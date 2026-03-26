# Stock Research Checklist

Pre-analysis checklist to ensure comprehensive coverage.

## Phase 1: Business Understanding

- [ ] What does the company do? (1-2 sentence summary)
- [ ] How does it make money? (Revenue segments)
- [ ] Who are the customers? (B2B/B2C, target market)
- [ ] What is the competitive advantage? (Moat)
- [ ] Who are the main competitors?

## Phase 2: Financial Health

- [ ] Current price and 52-week range
- [ ] Market cap and enterprise value
- [ ] Revenue growth (YoY, 3-year CAGR)
- [ ] Profit margins (gross, operating, net)
- [ ] **분기별 재무 추이** (최근 4~5분기 매출, 영업이익, EPS, EBITDA)
- [ ] **EPS 시장별 기준 병기** (미국: GAAP+Non-GAAP / 한국: 연결+별도)
- [ ] Balance sheet health (debt ratio, cash position)
- [ ] **재무 건전성 지표**: Current Ratio, FCF Yield
- [ ] Cash flow (operating, free cash flow)
- [ ] **지역별 매출 비중** (해외 매출 비율 및 성장률)

## Phase 3: Valuation

- [ ] **핵심 밸류에이션 세트 (전부 필수)**:
  - [ ] P/E (TTM) + Forward P/E
  - [ ] PEG
  - [ ] P/S + EV/Sales
  - [ ] EV/EBITDA
  - [ ] FCF Yield
  - [ ] Beta
  - [ ] Div Yield
- [ ] EPS Actual (GAAP + Non-GAAP) + Forward EPS Estimate
- [ ] **연도별 밸류에이션 추이** (과거 3~5년 P/E, EV/Revenue)
- [ ] **Peer 정량 비교** (경쟁사 2~3개: P/E, EV/Sales, 매출성장률, Gross Margin 테이블)
- [ ] Historical valuation range

## Phase 4: Industry-Specific Metrics

- [ ] Identify relevant sector from `sector-metrics-guide`
- [ ] Collect industry-specific KPIs
- [ ] EPS/회계 기준 차이 확인 (시장 가이드 참조)
- [ ] Compare to industry benchmarks

## Phase 5: Ownership & Sentiment

- [ ] Insider transactions (last 3-6 months)
- [ ] Institutional ownership changes
- [ ] Short interest and changes
- [ ] Analyst ratings distribution
- [ ] Average price target vs current price

## Phase 6: Recent Developments & Earnings Call

- [ ] Latest earnings highlights
- [ ] Management guidance
- [ ] **어닝콜 Q&A 핵심** (경영진 강조 포인트, 애널리스트 핵심 질문)
- [ ] Recent news and announcements
- [ ] M&A activity
- [ ] Product launches or strategic changes
- [ ] Regulatory developments

## Phase 7: Risk Assessment

- [ ] Business model risks
- [ ] Competitive risks
- [ ] Financial risks (debt, dilution)
- [ ] Regulatory risks
- [ ] Management risks
- [ ] Macro risks (rates, economy)

## Phase 8: Management Quality

- [ ] CEO background and track record
- [ ] Tenure and stability
- [ ] Insider ownership percentage
- [ ] Recent insider buying/selling
- [ ] Compensation alignment
- [ ] Communication quality

## Common Oversights

Things frequently missed in template-driven analysis:

| Category | What to Check |
|----------|---------------|
| Share dilution | YoY change in shares outstanding |
| EPS 기준 차이 | 미국: GAAP vs Non-GAAP / 한국: 연결 vs 별도 |
| Quarterly trends | 분기별 매출/이익 추이 (계절성, 가속/감속 패턴) |
| Geographic mix | 지역별 매출 비중 및 성장률 차이 |
| Sector context | Why is sector up/down right now? |
| Management quality | Co-CEO structures, founder status |
| Timing | Why now? What's the catalyst? |
| Hidden risks | Off-balance sheet items, pension obligations |
| Earnings call misses | 경영진이 답변 회피한 질문, 정량화 거부한 항목 |

## Research Sources

### Research Sources
시장별 가이드 파일에 정의된 소스를 사용:
- **미국**: `references/us-market-guide.md` (SEC EDGAR, Yahoo Finance, Finviz 등)
- **한국**: `references/kr-market-guide.md` (DART, 네이버증권, FnGuide 등)

## Phase 9: Chart Generation

- [ ] **필수**: 분기별 매출/EPS 추이 차트 (Plotly bar+line)
- [ ] **필수**: 연간 매출/순이익 성장 차트 (Plotly grouped bar)
- [ ] **필수**: 매출 구성 도넛 차트 (세그먼트 또는 지역)
- [ ] **조건부**: 손익 워터폴 (흑자 기업)
- [ ] **조건부**: 밸류에이션 추이 라인 차트 (데이터 있을 때)
- [ ] **조건부**: 부채/레버리지 차트 (고레버리지)

차트 템플릿: `references/chart-templates.md`

## Output Quality Check

Before finalizing analysis:

- [ ] All template sections completed
- [ ] Industry-specific metrics included
- [ ] GAAP vs Non-GAAP explained (if applicable)
- [ ] Risks clearly identified
- [ ] Investment thesis stated
- [ ] Action items defined
- [ ] Sources cited
