---
name: Sector Metrics Guide
description: This skill should be used when the user asks about "industry-specific metrics", "sector KPIs", "what metrics matter for [industry]", "GAAP vs non-GAAP", "how to evaluate [sector] stocks", or when analyzing stocks in specific sectors like asset managers, REITs, SaaS, banks, biotech, or energy. Provides comprehensive sector-specific financial metrics and benchmarks.
version: 1.0.0
---

# Sector Metrics Guide

## Overview

Different industries require different evaluation metrics. GAAP financial statements may not capture the true economics of specialized businesses. This guide provides the key performance indicators (KPIs) that investors actually use for each sector.

## Why This Matters

Standard metrics can be misleading:

| Sector | GAAP Problem | Better Metric |
|--------|--------------|---------------|
| Asset Managers | Stock comp distorts earnings | FRE, DE |
| REITs | Depreciation understates value | FFO, AFFO |
| SaaS | Growth investment looks like losses | ARR, Rule of 40 |
| Biotech | No revenue = no traditional metrics | Pipeline value |
| BDCs | Unrealized gains inflate income | NII |

## Quick Sector Reference

### Financial Services
- **Asset Managers**: FRE margin, Permanent capital %, Fee-paying AUM
- **BDCs**: NII, NAV discount, Dividend coverage
- **Banks**: NIM, CET1 ratio, Efficiency ratio
- **Insurance**: Combined ratio, Book value growth

### Real Estate
- **Equity REITs**: FFO, AFFO, Occupancy, WALT
- **Mortgage REITs**: Book value, Spread, Leverage

### Technology
- **SaaS**: ARR, NRR, Rule of 40, CAC payback
- **Semiconductors**: Gross margin, Book-to-bill

### Healthcare
- **Biotech**: Pipeline stage, Runway, Burn rate
- **Pharma**: Patent cliff, R&D ratio

### Energy
- **Oil & Gas**: Breakeven price, FCF yield, Reserve replacement
- **MLPs**: DCF, Distribution coverage

### Consumer
- **Retail**: Same-store sales, Inventory turnover
- **E-commerce**: GMV, Take rate

### Industrials
- **Aerospace/Defense**: Backlog, Book-to-bill, Gov contract %

## How to Use

1. **Identify the sector** - What industry does the company operate in?
2. **Find relevant metrics** - Consult detailed guides in references/
3. **Collect data** - Earnings releases often report these metrics
4. **Compare to benchmarks** - Use "good level" standards from the guides
5. **Note GAAP gaps** - Document where GAAP differs from reality

## Detailed Sector Guides

For comprehensive metric definitions, benchmarks, and examples:

- **`references/financial-sector.md`** - Asset managers, BDCs, banks, insurance
- **`references/real-estate-sector.md`** - REITs, mortgage REITs
- **`references/tech-sector.md`** - SaaS, semiconductors
- **`references/healthcare-sector.md`** - Biotech, pharma, medical devices
- **`references/energy-sector.md`** - Oil/gas, MLPs
- **`references/consumer-industrial.md`** - Retail, e-commerce, aerospace

## Common Pitfalls

1. **Using P/E for loss-making SaaS** - Use P/S or EV/ARR instead
2. **GAAP earnings for REITs** - FFO is the standard
3. **Net income for asset managers** - FRE/DE are core metrics
4. **Revenue for biotech** - Pipeline value matters more
5. **Ignoring share dilution** - Check YoY share count change

## Integration with Analysis Workflow

When using with `stock-analysis-workflow`:

1. First identify the company's sector
2. Load relevant metrics from this guide
3. Add metrics to the "Industry-Specific Metrics" template section
4. Note any GAAP vs Non-GAAP differences
5. Compare to sector benchmarks

## Representative Companies by Sector

| Sector | Examples |
|--------|----------|
| Asset Managers | BX, APO, ARES, KKR, OWL |
| BDCs | ARCC, OBDC, MAIN, HTGC |
| Banks | JPM, BAC, WFC, USB |
| Insurance | BRK.B, PGR, ALL, TRV |
| REITs | O, AMT, PLD, SPG, EQIX |
| SaaS | CRM, NOW, SNOW, DDOG |
| Semiconductors | NVDA, AMD, AVGO, TSM |
| Biotech | AMGN, GILD, VRTX, REGN |
| Pharma | JNJ, PFE, MRK, ABBV |
| Oil/Gas | XOM, CVX, COP, EOG |
| MLPs | EPD, ET, WMB, KMI |
| Retail | AMZN, WMT, COST, HD |
| Aerospace | BA, LMT, RTX, NOC |
