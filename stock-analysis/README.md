# Stock Analysis Plugin

주식 종목분석 워크플로우 자동화 플러그인입니다. 체계적인 조사 프로세스와 업종별 핵심지표 가이드를 제공합니다.

## Features

- **자유 조사 → 템플릿 보완** 워크플로우
- **업종별 핵심지표 가이드** (10개 섹터)
- **밸류에이션 적정가 산출** (기업 유형별 2~3개 방법론 교차 적용)
- **자동화된 웹 리서치** 에이전트
- **표준 분석 템플릿** 제공

## Installation

```bash
# 플러그인 디렉토리에서 실행
claude --plugin-dir /path/to/stock-analysis
```

## Commands

### `/stock-analysis:analyze [ticker] [output-path]`

종목분석 워크플로우를 시작합니다.

```bash
/stock-analysis:analyze AAPL
/stock-analysis:analyze OWL D:\Documents\StockAnalysis
```

**기능:**
- 웹 검색을 통한 기업 조사
- 재무 데이터 수집
- 업종별 핵심지표 적용
- 밸류에이션 적정가 산출 (기업 유형별 방법론 자동 선택)
- 분석 문서 생성

### `/stock-analysis:update [ticker] [existing-file-path]`

기존 분석 문서를 최신 정보로 갱신합니다.

```bash
/stock-analysis:update OWL D:\Documents\StockAnalysis\블루오울캐피탈.md
/stock-analysis:update AAPL ./03_Resources/주식분석/종목분석/애플.md
```

**기능:**
- 기존 분석 문서 읽기 및 마지막 분석일 확인
- 최근 뉴스, 실적, 가격 변동 조사
- 적정가 재산출 (주가 15%+ 변동, 신규 실적 등 트리거 시)
- 변경된 섹션만 선택적 업데이트
- 업데이트 이력 추적

## Skills

### stock-analysis-workflow

종목분석 프로세스 가이드를 제공합니다.

**트리거 예시:**
- "종목 분석해줘"
- "이 회사 조사해줘"
- "투자 분석 시작"

### sector-metrics-guide

업종별 핵심 재무지표를 제공합니다.

**지원 섹터:**
| 섹터 | 핵심 지표 |
|------|----------|
| 자산운용사 | FRE, DE, 영구자본 비중 |
| BDC | NII, NAV 할인율 |
| 은행 | NIM, CET1 |
| 보험 | Combined Ratio |
| 리츠 | FFO, AFFO |
| SaaS | ARR, NRR, Rule of 40 |
| 반도체 | Gross Margin, Book-to-Bill |
| 바이오 | 파이프라인, Runway |
| 석유/가스 | FCF Yield, 손익분기유가 |
| 항공/방산 | Backlog, Book-to-Bill |

**트리거 예시:**
- "이 업종의 핵심 지표가 뭐야?"
- "GAAP vs Non-GAAP 차이"
- "SaaS 회사 어떻게 평가해?"

## Agent

### stock-researcher

자동으로 종목 데이터를 수집하는 에이전트입니다.

**수집 항목:**
- 기업 개요 및 사업모델
- 재무 데이터 및 밸류에이션
- 최근 뉴스 및 발표
- 내부자 거래 및 애널리스트 의견
- 경쟁사 비교
- 밸류에이션 적정가 산출 (기업 유형별 방법론 자동 선택)

**사용 예시:**
```
"AAPL 리서치해줘"
"Blue Owl Capital 정보 모아줘"
```

## Workflow

### 신규 분석

```
1. 자유 조사 (stock-researcher 에이전트 또는 직접)
   ↓
2. 업종별 지표 확인 (sector-metrics-guide 스킬)
   ↓
3. 밸류에이션 적정가 산출 (기업 유형별 2~3개 방법론)
   ↓
4. 템플릿 적용 (stock-analysis-workflow 스킬)
   ↓
5. 문서 생성
```

### 기존 분석 갱신

```
1. 기존 문서 로드 (/stock-analysis:update)
   ↓
2. 마지막 분석일 이후 변경사항 조사
   ↓
3. 적정가 재산출 (트리거 조건 충족 시)
   ↓
4. 변경된 섹션만 업데이트
   ↓
5. 업데이트 이력 기록
```

## File Structure

```
stock-analysis/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── analyze.md
│   └── update.md
├── agents/
│   └── stock-researcher.md
├── skills/
│   ├── stock-analysis-workflow/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── analysis-template.md
│   │       └── research-checklist.md
│   └── sector-metrics-guide/
│       ├── SKILL.md
│       └── references/
│           ├── financial-sector.md
│           ├── real-estate-sector.md
│           ├── tech-sector.md
│           ├── healthcare-sector.md
│           ├── energy-sector.md
│           └── consumer-industrial.md
└── README.md
```

## Version History

- **1.3.1** - report 커맨드 제거 (analyze가 리서치+문서화 통합 수행)

- **1.3.0** - 리서치 품질 강화 (Investing.com Pro Research 수준 대응)
  - 에이전트/체크리스트: 분기별 재무 추이, GAAP/Non-GAAP EPS 병기, 재무 건전성 지표, 지역별 매출 비중
  - 에이전트/템플릿: 어닝콜 Q&A 핵심 (Bullish/Bearish/Misses), SWOT 분석 섹션
  - update 커맨드: 분기 재무 갱신, 어닝콜 Q&A, SWOT 업데이트 반영

- **1.2.1** - stock-researcher 에이전트에 밸류에이션 적정가 산출 단계 추가
  - 에이전트 Phase 8: 기업 유형별 방법론 자동 선택 및 적정가 범위 산출
  - 에이전트 Output Format에 Fair Value Estimation 섹션 추가
  - rNPV 가이드 (프리레버뉴/바이오 기업용) 포함

- **1.2.0** - 밸류에이션 적정가 산출 기능 추가
  - analyze: Phase 6 — 기업 유형별 방법론 자동 선택 및 적정가 범위 산출
  - update: Phase 3.5 — 트리거 조건(주가 15%+, 신규 실적 등) 충족 시 적정가 재산출
  - 분석 템플릿에 적정가 산출 섹션 추가
  - 지원 방법론: DCF, rNPV, P/E Comp, EV/Sales, DDM, Backward DCF 등

- **1.1.0** - Update command 추가
  - 3 Commands: analyze, update, report (report는 1.3.1에서 제거)
  - 기존 분석 문서 갱신 워크플로우 지원
  - 업데이트 이력 추적 기능

- **1.0.0** - Initial release
  - 2 Skills: stock-analysis-workflow, sector-metrics-guide
  - 2 Commands: analyze, report (report는 1.3.1에서 제거)
  - 1 Agent: stock-researcher

## Author

elhaz

## License

MIT
