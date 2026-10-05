---
name: analyze
description: Start comprehensive stock analysis for a given ticker
argument-hint: "[ticker] [output-path]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Agent
---

# Stock Analysis Command

2-Agent 파이프라인으로 종목분석 문서를 생성한다.

## Arguments

- `ticker` (required): Stock ticker symbol (e.g., AAPL, MSFT, 051910)
- `output-path` (optional): Path to save the analysis document. 생략 시 `$OBSIDIAN_VAULT/03_Resources/주식분석/종목분석/{회사명}.md` (`OBSIDIAN_VAULT` 미설정 시 현재 작업 디렉토리 기준 상대경로). 회사명은 해당 디렉토리의 기존 파일 관례를 따른다 (예: `AMD.md`, `ASML홀딩.md`)

## Workflow

### Step 0: 이전 판 보관

출력 경로에 문서가 이미 있으면 아래 "이전 판 보관" 의 `archive` 를 먼저 실행한다.

### Step 1: Data Collection (stock-data-collector, Sonnet)

`stock-data-collector` 에이전트를 호출하여 정량 데이터를 수집한다.

**에이전트 프롬프트에 포함할 내용**:
- 티커: {ticker}
- findata 스크립트 경로 `${CLAUDE_PLUGIN_ROOT}/scripts/fdp_fundamentals.py` (미국 종목은 이것부터 — 없는 것만 웹)
- 수집 이유 `--reason "종목 분석"` (findata 활동 기록의 "왜". 사용자가 목적을 말했으면 그것을 짧게, 예: `"종목 분석 · 매수 검토"`)
- 시장 가이드 참조 지시 (티커 형식에 따라 us/kr, 절대경로로)
- 필수 수집 항목 전체 나열 (밸류에이션 11개, 분기별 재무, 연도별 추이, Peer 비교, 수급)

**에이전트 반환**: 구조화된 데이터 (테이블 형태)

### Step 2: Analysis & Document (stock-analyst, 세션 모델)

`stock-analyst` 에이전트를 호출하여 분석 + 문서 작성한다.

**에이전트 프롬프트에 포함할 내용**:
- Step 1에서 수집된 데이터 전체 (복사하여 전달)
- 출력 파일 경로: {output-path}
- 참고 파일 절대경로: 시장 가이드 · `chart-templates.md` · 해당 섹터 `sector-metrics-guide/references/*.md` (첫 턴에 병렬 Read)
- 필수 산출물: 경쟁 분석, 어닝콜 Q&A, SWOT, 적정가, Plotly 차트

**에이전트 산출물**: 완성된 종목분석 .md 파일

### Step 3: 이력 링크

`link` 를 실행해 최신본 끝에 이전 분석 링크를 붙인다 (이력이 없으면 절을 만들지 않는다).

### Step 4: 데일리로그 한 줄

문서를 다 쓰면 데일리로그 오늘 `##### 개인` 칸에 링크를 남긴다. 볼트의 `.scripts/dailylog-scrap.py` 가 있는 환경(NAS)에서만 하고, 없으면 건너뛴다 (`.scripts` 는 동기화되지 않는 로컬 전용). 같은 날 이미 있으면 스크립트가 건너뛴다. 실패해도 무시한다.

```bash
S="${OBSIDIAN_VAULT:-.}/.scripts/dailylog-scrap.py"
[ -f "$S" ] && python3 "$S" --section 개인 "{문서 경로}::{문서명} 종목분석"
```

### 이전 판 보관 (날짜별 이력)

최신본은 제자리에 두고, 덮어쓰기 전 판을 `종목분석/이력/{문서명}/{updated 날짜}.md` 로 보관한다. 이력본은 태그가 `종목분석이력` 으로 바뀌어 대시보드에 겹쳐 뜨지 않는다.

```bash
H="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/elhaz-plugins/stock-analysis/*/ | sort -V | tail -1)}"; H="${H%/}/scripts/analysis_history.py"
python3 "$H" archive "{문서 경로}"    # 쓰기 전 — 문서가 없으면 아무것도 안 함
python3 "$H" link "{문서 경로}"       # 쓰기 후 — 끝에 `## 이전 분석` 링크 목록
```

## 오케스트레이션 예시

```
1. stock-data-collector 호출:
   "Collect all quantitative data for {TICKER}.
    First run: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/fdp_fundamentals.py {TICKER} --peers {P1},{P2},{P3} --reason "종목 분석"
    Copy its tables as-is; web-search only what its '### fdp 상태' lists, then record gaps.
    Read ${CLAUDE_PLUGIN_ROOT}/skills/stock-analysis-workflow/references/us-market-guide.md (or kr-market-guide.md).
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
    In your first turn, Read in parallel: ${CLAUDE_PLUGIN_ROOT}/skills/stock-analysis-workflow/references/chart-templates.md,
    the market guide, and ${CLAUDE_PLUGIN_ROOT}/skills/sector-metrics-guide/references/{sector}.md.
    Do not re-search numbers already in the data. Write the document in one Write."
```

## Example Usage

```
/stock-analysis:analyze AAPL
/stock-analysis:analyze NVDA 03_Resources/주식분석/종목분석/엔비디아.md
/stock-analysis:analyze 051910 03_Resources/주식분석/종목분석/LG화학.md
```
