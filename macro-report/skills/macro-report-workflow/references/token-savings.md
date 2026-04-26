# 토큰 절감 측정 (#7)

financial-data-platform 통합으로 인한 토큰 절감 효과를 실측·기록하기 위한 표.

## A/B 모드 정의

- **A 모드 (baseline, capabilities OFF)**: 기존 WebSearch-only 경로. `--no-api` 인자 또는 `MACRO_SKIP_API=1` 환경변수로 강제.
- **B 모드 (treatment, capabilities ON)**: macro-scanner 가 `/api/meta/capabilities` 부터 시작하는 신규 경로. **현재 기본값**.

같은 날 같은 보고서 유형으로 A/B 한 번씩 실행해 페어를 만든다. 시점 차이로 인한 데이터 편차는 노이즈로 간주.

## 측정 방법

각 실행 후 macro-scanner 가 `scan_data_path` 말미에 `## 수집 메타` 섹션을 남긴다. 그 메타에서 아래 컬럼을 발췌해 표에 한 행 추가.

- `api_calls`, `web_searches` — 호출 카운트 (정확)
- `api_kb`, `web_kb` — 응답 본문 크기 합 (KB). 실측 가능하면 실측, 어려우면 빈칸.
- `scan_data_kb` — 최종 `.scan/[type]_[date].md` 파일 크기 (KB). 다운스트림 writer 입력의 1차 근사치.
- `capabilities_used` — B 모드에서 capabilities fetch 가 실제 성공했는가. 자동 degrade 시 `false`.
- `degrade_reason` — capabilities 호출 실패로 자동 fallback 한 경우 이유. 정상 A 모드에서는 빈칸.

## 측정 기록표

| 실행일 | 모드 | report | api_calls | web_searches | api_kb | web_kb | scan_data_kb | capabilities_used | 메모 |
|--------|------|--------|----------:|-------------:|-------:|-------:|-------------:|:------------------:|------|
| 2026-04-26 | B | liquidity | 14 | 14 | — | — | 20.0 | true | scanner 79,767 tok / 357s / 42 tool uses. 첫 페어 |
| 2026-04-26 | A | liquidity | 0 | 22 | 0 | ~80 | 19.0 | false | scanner 90,143 tok / 488s / 46 tool uses. B 대비 토큰 -11.5%, 속도 -26.8% |

### 페어 1 (2026-04-26 liquidity) 관찰

- **토큰 절감 -11.5%** (scanner 단계). web_searches 14→22 증가가 capabilities fetch 비용을 일부 상쇄.
- **속도 절감 -26.8%** 가 더 두드러짐 — API 결정적 응답 vs WebSearch 검색+fetch 직렬 지연.
- 품질: B가 정량값 정확 (RRP $0.082M, TGA $1.006조 등). A는 수치 추정·보수적.
- **API 함정 발견**: `/api/indicators/{symbol}?limit=N` 만으로 호출 시 1959년 데이터 반환. `start_date` 명시 필수. 배치 가격 API 도 동일 — financial-data-platform 측 별도 이슈 등록.

## 분석 가이드

- 페어 5쌍 이상 쌓이면 평균 절감률 산출 (B/A scan_data_kb 기준).
- 항목별 분해가 필요하면 scan_data 파일에 항목별 `[출처: API|WebSearch]` 태그가 부착되어 있으니 grep 으로 분리 집계.
- 자동 누적·시각화는 financial-data-platform #15 (data_gaps 피드백 루프) 와 묶어 후속 검토.

## 관련

- financial-data-platform [issue #6](https://git.xhhan.com/xhh/financial-data-platform/issues/6) — 시범 전환 본 작업
- financial-data-platform [issue #7](https://git.xhhan.com/xhh/financial-data-platform/issues/7) — 토큰 절감 측정
- financial-data-platform [issue #15](https://git.xhhan.com/xhh/financial-data-platform/issues/15) — data_gaps 피드백 루프 (후행)
