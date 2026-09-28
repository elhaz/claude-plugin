# 크로스에셋 레짐 분석 — 질문 템플릿

> macro-scanner에게 전달되는 데이터 수집 가이드

## 수집 범위

- 기준: 현재일
- 대상: 크로스에셋 상관관계 기반 시장 레짐 진단

## 수집 항목 (9개)

1. **주식-채권 상관관계** — S&P 500 vs TLT 상관계수 (30일/60일 롤링). 양(+)이면 인플레이션 주도, 음(-)이면 성장 주도. 10Y 국채 수익률 추이 포함
2. **VIX-주가 관계** — VIX 수준, VIX-SPX 상관계수, VIX 선물 기간구조(콘탱고/백워데이션), SPY IV Percentile
3. **달러-원자재-신흥국 삼각** — DXY, WTI/Brent, 금, 구리, IEMG 수준 + 상호 상관관계 변화. 전통적 역상관 유지/붕괴 여부
4. **팩터 간 상관관계** — VLUE, SPLV, MTUM, QUAL YTD + 1개월 성과.
5. **섹터 간 상관관계 이상** — 경기순환(XLE/XLI) vs 방어(XLU/XLP) YTD + 1개월. "Strange Couple" (동시 강세) 여부와 해소 방향
6. **금-실질금리 관계** — 금 가격 vs 10Y TIPS 실질수익률. 역상관 유지/붕괴, 붕괴 시 원인(중앙은행 매입, 지정학 프리미엄)
7. **크레딧 스프레드-주식 괴리** — IG/HY OAS vs S&P 500 YTD. 스프레드 확대 + 주식 버팀 = 주식 과낙관. 반대 = 단기 과매도
8. **글로벌 자금 흐름** — TIC 순흐름(민간/공식), 비미국 ETF 유입 규모, 통화 헤징 비용 변화, Great Rotation 지표
9. **핵심 매크로 데이터** — GDP, PCE, CPI, 실업률, ISM, LEI 최신값·전기 대비·발표일. 레짐 분류·전환 판단은 하지 않는다 (writer 몫)

## 주요 데이터 소스

- FRED (국채, TIPS, 크레딧 스프레드)
- CBOE (VIX, 기간구조)
- Yahoo Finance / Google Finance (팩터/섹터 ETF 성과)
- World Gold Council (금 ETF 흐름)
- Treasury.gov (TIC)
- Atlanta Fed GDPNow
- BEA (GDP), BLS (고용/CPI), ISM
