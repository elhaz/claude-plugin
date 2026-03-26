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
  - TodoWrite
---

# Stock Analysis Update Command

Update an existing stock analysis document with recent developments and changes.

## Arguments

- `ticker` (required): Stock ticker symbol (e.g., AAPL, MSFT, OWL)
- `existing-file-path` (required): Path to the existing analysis document

## Workflow

### Phase 1: Load Existing Analysis

1. **Read the existing document**
   - Parse frontmatter for metadata (ticker, sector, created, updated)
   - Identify last analysis date from `updated` field
   - Note key metrics and thesis from previous analysis

2. **Extract key reference points**
   - Previous price and valuation metrics
   - Investment thesis and conviction level
   - Identified risks and catalysts
   - Action items from last analysis

### Phase 2: Research Recent Developments

Focus on changes **since the last analysis date**:

1. **Price & Valuation Changes**
   - Search: "{Ticker} stock price {current date}"
   - Compare to previous analysis price
   - Calculate % change

2. **Earnings & Financials**
   - Search: "{Company} earnings {quarter} {year}"
   - Check if new earnings released since last update
   - Note any guidance changes

3. **News & Announcements**
   - Search: "{Company} news {month} {year}"
   - Filter for material developments only
   - M&A, management changes, strategic shifts

4. **Insider Activity**
   - Search: "{Ticker} insider transactions {month} {year}"
   - New insider buying or selling patterns

5. **Analyst Updates**
   - Search: "{Ticker} analyst rating upgrade downgrade"
   - Price target changes

### Phase 3: Identify Material Changes

Categorize findings by impact:

| Impact Level | Examples | Action |
|--------------|----------|--------|
| **High** | Earnings miss/beat, guidance change, M&A | Update thesis |
| **Medium** | Price movement >10%, analyst changes | Update metrics |
| **Low** | Minor news, small price changes | Note in history |

### Phase 3.5: Valuation & Fair Price Re-estimation

기존 적정가 산출이 있으면 최신 데이터로 재산출, 없으면 신규 산출.

**방법론 참고**: Vault 내 `밸류에이션 적정가 산출 방법론` 문서가 있으면 Read하여 참고.

**재산출 트리거** (아래 중 하나라도 해당 시):
- 주가 15%+ 변동
- 새 실적 발표 (매출/이익 변동)
- 시나리오 확률 변동이 필요한 중대 뉴스 (인증 진행, M&A 등)
- 희석 이벤트 (유상증자, 전환사채 등)

**재산출 절차**:
1. 기존 적정가 산출 섹션 확인 (이전 방법론/수치 파악)
2. 변경된 입력값 업데이트 (주가, EPS, 매출, 현금, 주식수, 시나리오 확률 등)
3. 동일 방법론으로 재산출, 이전 적정가와 비교
4. 적정가 종합 테이블 업데이트

**적정가 섹션이 없는 기존 문서**: Phase 6 (analyze 커맨드) 절차를 따라 신규 산출 후 삽입. "밸류에이션 지표" 섹션 아래에 "적정가 산출" 서브섹션으로 추가.

### Phase 4: Update Document

1. **Update frontmatter**
   ```yaml
   updated: [current date]
   ```

2. **Update "현재 상태" section**
   - New price and valuation metrics
   - Performance since last analysis

3. **Add "최근 변경사항" section** (if not exists)
   - Date of update
   - Key changes identified
   - Impact assessment

4. **Update affected sections**
   - Only modify sections with material changes
   - Preserve unchanged content
   - Add notes for context

5. **Update "다음 액션" section**
   - Re-evaluate action items
   - Add new catalysts/deadlines

### Phase 5: Generate Update Summary

At the end of the document or in a comment, add:

```markdown
---

## 📋 업데이트 이력

### [YYYY-MM-DD] 업데이트
- **가격 변동**: $XX → $YY (±Z%)
- **주요 변경**: [핵심 변경사항 1-2줄]
- **투자의견 변화**: [유지/상향/하향]
```

## Update Frequency Guidelines

| Situation | Recommended Action |
|-----------|-------------------|
| Earnings released | Update within 1 week |
| >15% price move | Review and update |
| Major news | Update immediately |
| Routine check | Monthly or quarterly |

## Example Usage

```
/stock-analysis:update OWL D:\Documents\StockAnalysis\블루오울캐피탈.md
/stock-analysis:update AAPL ./03_Resources/주식분석/종목분석/애플.md
```

## Comparison Mode

When updating, always show before/after for key metrics:

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Price | $XX | $YY | ±Z% |
| P/E | XX | YY | ±Z |
| Market Cap | $XXB | $YYB | ±Z% |

## Edge Cases

- **Document not found**: Prompt user to run `/stock-analysis:analyze` first
- **Very old analysis (>6 months)**: Recommend full re-analysis instead
- **Ticker changed**: Note ticker change in update history
- **Company acquired**: Mark as archived, note acquisition details

## Tips

- Focus on material changes, not minor fluctuations
- Preserve the original investment thesis unless fundamentally challenged
- Use the update history to track your analysis evolution
- Cross-reference with `sector-metrics-guide` for industry context
