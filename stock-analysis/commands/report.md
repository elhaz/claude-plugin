---
name: report
description: Generate formatted stock analysis report from collected research
argument-hint: "[ticker] [output-path]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - TodoWrite
---

# Stock Report Generation Command

Generate a formatted stock analysis document from previously collected research data.

## Arguments

- `ticker` (required): Stock ticker symbol for the report
- `output-path` (required): Directory path to save the analysis document

## Prerequisites

This command assumes research has already been conducted. For fresh analysis, use `/stock-analysis:analyze` first.

If research data is available in context, this command will format it into the standard template.

## Template Structure

The report follows this structure:

```markdown
---
tags:
  - 종목분석
  - [섹터태그]
ticker: [TICKER]
sector: [섹터명]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
---

# [종목명] ([Company Name], [TICKER])

## 📊 현재 상태
## 📅 분기별 재무 추이
## 🏢 사업 모델 & 경쟁력
## 👨‍💼 CEO 정보
## 🔔 리스크 요인
## 📝 다음 액션
```

## Workflow

1. **Gather Research Data**
   - Check if research data exists in current context
   - If not, prompt user to run `/stock-analysis:analyze` first

2. **Load Template**
   - Use template from `references/analysis-template.md`

3. **Populate Sections**
   - Fill in all available data
   - Mark missing sections for follow-up

4. **Add Sector Metrics**
   - Reference `sector-metrics-guide` for industry-specific metrics
   - Include GAAP vs Non-GAAP notes where applicable

5. **Generate Document**
   - Create file at: `{output-path}/{ticker} 종목분석.md`
   - Use Korean formatting conventions

## Output Format

- **File name**: `{ticker} 종목분석.md` (e.g., `AAPL 종목분석.md`)
- **Encoding**: UTF-8
- **Format**: Obsidian-compatible markdown

## Example Usage

```
/stock-analysis:report AAPL D:\Documents\StockAnalysis
/stock-analysis:report OWL ./03_Resources/주식분석/종목분석
```

## Quality Checklist

Before finalizing the report:

- [ ] All basic information filled (ticker, price, market cap)
- [ ] Investment thesis criteria evaluated
- [ ] Industry-specific metrics included
- [ ] GAAP vs Non-GAAP differences noted (if applicable)
- [ ] Risks clearly identified
- [ ] CEO/management evaluated
- [ ] Action items defined
- [ ] Tags and frontmatter complete
