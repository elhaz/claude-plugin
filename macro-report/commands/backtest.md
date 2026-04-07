---
name: backtest
description: 추천 종목 이력의 기간별 가격을 갱신합니다
argument-hint: ""
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
  - mcp__brightdata__scrape_as_markdown
  - mcp__brightdata__scrape_batch
  - mcp__brightdata__search_engine
  - mcp__brightdata__search_engine_batch
---

# /macro-report:backtest

추천 종목 이력 파일의 빈 기간별 가격(1주후, 2주후, 1개월후, 3개월후)을 조사하여 채워넣는다.

## 대상 파일

`02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/추천 종목 이력.md`

## 워크플로우

### Step 1: 이력 파일 파싱

1. 추천 종목 이력 파일을 Read
2. 테이블에서 빈 기간 셀을 식별
3. 각 빈 셀에 대해 목표 날짜를 계산:
   - **1주후**: 보고서날짜 + 7일
   - **2주후**: 보고서날짜 + 14일
   - **1개월후**: 보고서날짜 + 30일
   - **3개월후**: 보고서날짜 + 90일
4. 목표 날짜가 **오늘 이전**인 것만 갱신 대상 (미래 날짜는 스킵)
5. 목표 날짜가 **주말/미국 증시 휴장일**이면 직전 영업일 종가 사용
   - **주말**: 토/일
   - **미국 증시 정기 휴장일** (NYSE/NASDAQ):
     - New Year's Day (1/1, 주말 시 인접 평일)
     - Martin Luther King Jr. Day (1월 셋째 월요일)
     - Presidents Day / Washington's Birthday (2월 셋째 월요일)
     - **Good Friday** (부활절 직전 금요일 — 매년 날짜 변동, 종종 누락 주의)
     - Memorial Day (5월 마지막 월요일)
     - Juneteenth (6/19, 주말 시 인접 평일)
     - Independence Day (7/4, 주말 시 인접 평일)
     - Labor Day (9월 첫째 월요일)
     - Thanksgiving (11월 넷째 목요일) + 다음 날 단축거래(13:00 ET 마감)
     - Christmas Day (12/25, 주말 시 인접 평일)
   - 단축거래일(7/3, 11월 Thanksgiving 다음날, 12/24)도 종가는 정상 기록
   - 의심 시: stockanalysis.com history 페이지에 해당 날짜 행이 없으면 휴장일 → 직전 행 사용

### Step 2: 가격 조사

가격 조사는 다음 도구 중 **상황에 맞는 것**을 선택한다:

#### 옵션 A: Bright Data MCP (권장 — 빠르고 정확)

`mcp__brightdata__scrape_batch`로 stockanalysis.com 페이지를 일괄 스크래핑:

```
URL 패턴: https://stockanalysis.com/stocks/{ticker}/history/
한 번에 최대 10개 URL 처리 가능
```

장점:
- 봇 차단/JS 렌더링 자동 우회
- 페이지에 6개월치 OHLCV 표가 다 있어 여러 날짜를 한 번에 추출 가능
- 휴장일은 자동으로 표에서 빠져 있어 직전 영업일을 즉시 식별 가능

단점: Bright Data MCP가 설정되어 있어야 함

#### 옵션 B: web-search-agent (Sonnet) — 폴백

Bright Data MCP가 없거나 종목 수가 매우 많을 때:

**에이전트 프롬프트 구성:**
- 갱신 대상 종목+날짜 목록 전달
- "stockanalysis.com history 페이지에서 {ticker}의 {date} 종가 조회"
- 휴장일이면 직전 영업일 종가 사용
- TSV 형식으로 반환 요청

**효율화:**
- 종목 수가 많으면 10~15개씩 묶어 병렬 에이전트 실행
- 동일 종목의 여러 날짜는 한 번에 조회

#### 데이터 출처 우선순위

1. **stockanalysis.com `/stocks/{ticker}/history/`** (1순위)
   - 일단위 OHLCV 표가 깔끔하고 휴장일 누락이 명확
2. Yahoo Finance `/quote/{ticker}/history/` (2순위)
   - 종종 결측, 일부 종목은 splitsharp 미반영
3. Investing.com (3순위 — 최후 수단)
   - 형식 변동이 많아 파싱 불안정

### Step 3: 이력 파일 갱신

1. 조사된 가격으로 테이블의 빈 셀을 Edit으로 채움
2. 각 행을 정확히 매칭하여 편집 (보고서날짜 + 티커로 식별)
3. 이미 값이 있는 셀은 덮어쓰지 않음

### Step 4: 신규 추천 종목 추가 (선택)

최신 종합 보고서에 새로운 추천 종목이 있는지 확인:

1. `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/` 에서 가장 최근 **"YYYY-MM-DD 종합 분석 및 투자 판단.md"** 파일을 찾음
2. 해당 보고서의 **`## 목표 수익률 및 손절선` 섹션의 `### 개별 종목` 표**에서 추천 종목 추출
   - 표 컬럼: `종목 | 비중 | 손절선 | 목표가 | 업사이드`
   - 표에 등장하는 모든 티커가 후보 (단, ETF 제외 — EWY, EWJ, XLE, GLD, SGOV 등)
3. 이력에 없는 (보고서날짜 + 티커) 조합만 추가
4. 추천시점가는 보고서 작성일 직전 영업일 종가를 가격 조사 (Step 2 도구 재사용)
5. 목표가는 표의 `목표가` 컬럼 값 사용 (범위 표기 시 중간값, 원본은 비고)

### Step 5: S&P 500 데이터 갱신

추천 백테스트 대시보드의 `SP` 객체에 신규 보고서 날짜의 S&P 500 데이터가 없으면 추가:

1. `추천 백테스트.md`를 Read
2. `SP` 객체에서 누락된 보고서 날짜 확인
   - 형식: `"YYYY-MM-DD": [시점, 1w, 2w, 1m, 3m]`
   - 갱신은 두 가지 케이스:
     - **신규 날짜 행 추가**: 새 보고서 날짜의 시점가
     - **기존 행의 미도래 셀 채움**: 이전 보고서의 1w/2w/1m/3m 셀 (Step 1과 동일한 영업일 규칙 적용)
3. 해당 날짜의 S&P 500 가격을 가격 조사 (Step 2 도구 재사용, 티커 `^GSPC` 또는 `SPY`)
4. **일관성 검증** (중요):
   - 새 보고서 날짜의 `시점가`는 직전 보고서 행의 같은 날짜에 해당하는 셀(예: 7일 전 보고서의 1w 셀)과 **같은 값이어야 함**
   - 불일치 발견 시 사용자에게 보고하고 어느 값이 정확한지 확인 후 양쪽 동기화
   - 휴장일 보정 차이 또는 기록 오류로 인한 누적 불일치 방지
5. `SP` 객체에 값을 추가/수정

## 기록 규칙

- 추천시점가: 보고서 작성일 직전 영업일 종가 (보고서에 명시된 가격이 있으면 우선)
- 기간별 가격: 해당 날짜의 종가 (휴장일이면 직전 영업일)
- ETF(EWY, EWJ, XLE, GLD, SGOV 등) 제외, 개별 종목만
- 목표가 범위는 중간값, 원본은 비고에 표기
- 미도래 기간은 빈칸 유지

## Example Usage

```
/macro-report:backtest
```

보고서 생성 후, 또는 주기적으로(주 1회) 실행하여 이력을 최신 상태로 유지한다.
