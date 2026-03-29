# 시장 주도 업종 분석 — 질문 템플릿

> macro-scanner에게 전달되는 데이터 수집 가이드

## 수집 범위

- 기간: 현재일 기준 최근 2주
- 대상: 미국 ETF 시장 (AUM 10억 달러 이상)

## 수집 항목 (12개)

1. **순 자금 유입 Top 20** — 티커, ETF명, 유입액, 섹터/테마 분류
2. **ETF별 자금 유입 규모 + 변화율** — 전주/전월 대비 변화
3. **자금 유출 ETF + 원인** — 유출 상위 10개, 구조적 이동 vs 약세 매도 구분
4. **섹터별 자금 흐름** — XLE/XLF/XLK/XLU/XLP/XLI/XLV/XLB/XLY/XLC/XLRE YTD 성과 + 주간 흐름
5. **테마별 ETF 흐름** — 소프트웨어/AI(IGV), 방산(SHLD/ITA), 에너지, 금/귀금속, 암호화폐, 중국(KWEB) 등
6. **지역별 ETF 흐름** — EWY, VGK, EWJ, EEM, IEMG, KWEB, FXI, INDA, VXUS 등 YTD + 자금흐름
7. **팩터 ETF 흐름** — VLUE, SPLV, MTUM, QUAL, USMV, SCHD, VYM, RSP YTD + 자금흐름. 시장 팩터 선호도 해석 포함
8. **자금 흐름 선후관계** — 가격 역행 유입(선행), 가격 동행 유입(동행), 가격 추격 유입(후행) 구분
9. **스마트머니 vs 리테일** — Creation/Redemption 단위 데이터로 AP 활동 추적. 대량 생성 = 기관 매수, 대량 환매 = 기관 이탈. 레버리지 ETF(TQQQ/SOXL) 유입 = 리테일 투기
10. **ETF 공매도 비율 변화** — 자금 유출 + 공매도 증가 = 확신 약세. 자금 유입 + 공매도 높음 = 숏스퀴즈 잠재
11. **신규 ETF 상장/폐지** — 최근 2주 신규 상장 테마 (특정 테마 집중 = 과열 신호)
12. **ETF 옵션 시장** — SPY/QQQ Put/Call Ratio, 옵션 스큐, 0DTE 거래량 추이

## 주요 데이터 소스

- etf.com
- ETFdb.com
- ICI (Investment Company Institute) 주간 흐름
- Morningstar ETF Flows
- Seeking Alpha ETF Hub
- CBOE (옵션 데이터)
