# 미국 주식 분석 가이드 (US Market)

미국 주식(NYSE, NASDAQ) 분석 시 적용하는 시장 특수 사항.

## 회계 기준: US GAAP

### GAAP vs Non-GAAP EPS

미국 기업은 GAAP EPS와 Non-GAAP(Adjusted) EPS를 병행 공시한다.

**반드시 양쪽 모두 기재**하고 차이를 설명할 것.

| 항목 | 설명 |
|------|------|
| GAAP EPS | 법적 기준, SBC/무형자산 상각/구조조정 포함 |
| Non-GAAP EPS | 경영진 조정, 일회성 항목 제외 |
| 주요 차이 원인 | SBC(주식보상비용), 인수 관련 무형자산 상각, 구조조정 비용 |

**주의**: Non-GAAP이 GAAP의 2배 이상 차이나면 반드시 경고 표시.

### Forward EPS Estimate

미국 애널리스트 컨센서스는 대부분 Non-GAAP 기준. Forward P/E도 Non-GAAP EPS 기준으로 산출.

## 공시 체계

| 공시 | 내용 | 소스 |
|------|------|------|
| 10-K | 연간 보고서 | SEC EDGAR |
| 10-Q | 분기 보고서 | SEC EDGAR |
| 8-K | 주요 사건 공시 | SEC EDGAR |
| Form 4 | 내부자 거래 | SEC EDGAR |
| 13F | 기관 보유 현황 (분기) | SEC EDGAR |
| Proxy Statement (DEF 14A) | 경영진 보상, 의결 안건 | SEC EDGAR |

## 내부자 거래 (Insider Activity)

- **Form 4** 기반 — CEO, CFO, 이사 등의 매수/매도
- **10b5-1 Plan**: 사전 계획된 매도 (자동 실행) — 신호로서 가치 낮음
- **Open Market Buy**: 경영진이 자발적으로 매수 — 강한 신호
- **Cluster Buy**: 여러 내부자가 동시에 매수 — 매우 강한 신호

## 공매도 (Short Interest)

- **Short Float %**: 유통주식 대비 공매도 비율
- 10% 이상: 높은 베어리시 심리
- **Days to Cover**: 공매도 주식수 / 평균 거래량
- 3일 이상: 숏스퀴즈 가능성 고려

## 어닝콜 (Earnings Call)

미국 기업은 분기마다 어닝콜을 개최하며, 경영진 프레젠테이션 + 애널리스트 Q&A로 구성.

**수집 항목**:
- Bullish Highlights (경영진 강조 포인트)
- Bearish Highlights (성장 둔화, 마진 압박 등)
- Q&A 핵심 (애널리스트 질문 중 가장 중요한 이슈)
- Misses (답변 회피하거나 정량화 거부한 항목)

## 밸류에이션 특수성

- **PEG**: 미국 시장에서 널리 사용. Forward P/E / EPS Growth Rate
- **FCF Yield**: 미국 기업은 FCF 중심 평가가 일반적
- **자사주 매입(Buyback)**: 주주환원의 주요 수단, Buyback Yield 참고
- **배당**: 분기 배당이 일반적 (연 4회)

## 검색 소스

| 소스 | 용도 |
|------|------|
| SEC EDGAR | 공식 공시 |
| Yahoo Finance | 밸류에이션, 재무 |
| StockAnalysis.com | 컨센서스, Forecast |
| Finviz | 종합 지표 |
| MarketBeat | 내부자 거래, 기관 |
| Seeking Alpha | 어닝콜 트랜스크립트 |

## 통화

- 모든 금액: **USD ($)** 기준
- 시가총액 단위: $B (billion), $M (million)
