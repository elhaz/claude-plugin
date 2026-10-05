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
  - Bash
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
3. 아래 "이전 판 보관" 의 `archive` 실행 — 갱신 전 판을 이력으로 남긴다

### Step 1: Delta Data Collection (stock-data-collector, Sonnet)

`stock-data-collector` 에이전트를 호출하되, **마지막 분석일 이후 변경분**에 초점.

**에이전트 프롬프트에 포함**:
- 티커 + 마지막 분석일
- findata 스크립트 경로 `${CLAUDE_PLUGIN_ROOT}/scripts/fdp_fundamentals.py` — 가격·밸류에이션·분기 실적·컨센서스·내부자는 여기서 (미국 종목)
- 수집 이유 `--reason "업데이트"` (findata 활동 기록의 "왜". 계기가 있으면 짧게 덧붙인다, 예: `"업데이트 · 3분기 실적"`)
- "이 날짜 이후의 변경사항 중심으로 수집"
- 현재 가격/밸류에이션 세트 갱신
- 새 분기 실적 발표 여부
- 애널리스트 목표가 변동
- 내부자/수급 변동

### Step 2: Analysis & Update (stock-analyst, 세션 모델)

`stock-analyst` 에이전트를 호출하여 기존 문서를 갱신.

**에이전트 프롬프트에 포함**:
- 기존 문서 경로 (analyst 가 직접 Read — 전문을 붙여 넣지 않는다)
- Step 1에서 수집된 델타 데이터
- 갱신 지시:
  - frontmatter `updated` / `마지막수정일` 날짜 갱신
  - frontmatter `현재가` 갱신 (분석 시점 주가, 숫자만, KRW는 정수/USD는 소수점 2자리)
  - 적정가 재산출 시 frontmatter `적정가하단` / `적정가상단` 갱신
  - frontmatter `sector` 값이 허용 목록(stock-analyst.md 참조)에 맞는지 확인, 불일치 시 수정
  - 밸류에이션 지표 갱신
  - 새 분기 데이터 추가 (테이블 + 차트)
  - SWOT 갱신 (신규 이벤트 반영)
  - 적정가 재산출 트리거 체크 (주가 15%+ 변동, 신규 실적)
  - 업데이트 이력 추가

### Step 3: 이력 링크

갱신이 끝나면 `link` 를 실행한다.

### Step 4: 데일리로그 한 줄

문서를 다 쓰면 데일리로그 오늘 `##### 개인` 칸에 링크를 남긴다. 볼트의 `.scripts/dailylog-scrap.py` 가 있는 환경(NAS)에서만 하고, 없으면 건너뛴다 (`.scripts` 는 동기화되지 않는 로컬 전용). 같은 날 이미 있으면 스크립트가 건너뛴다. 실패해도 무시한다.

```bash
S="${OBSIDIAN_VAULT:-.}/.scripts/dailylog-scrap.py"
[ -f "$S" ] && python3 "$S" --section 개인 "{문서 경로}::{문서명} 종목분석 갱신"
```

### 이전 판 보관 (날짜별 이력)

최신본은 제자리에 두고, 덮어쓰기 전 판을 `종목분석/이력/{문서명}/{updated 날짜}.md` 로 보관한다. 이력본은 태그가 `종목분석이력` 으로 바뀌어 대시보드에 겹쳐 뜨지 않는다.

```bash
H="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/elhaz-plugins/stock-analysis/*/ | sort -V | tail -1)}"; H="${H%/}/scripts/analysis_history.py"
python3 "$H" archive "{문서 경로}"    # 쓰기 전 — 문서가 없으면 아무것도 안 함
python3 "$H" link "{문서 경로}"       # 쓰기 후 — 끝에 `## 이전 분석` 링크 목록
```

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
