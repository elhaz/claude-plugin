# 데이터 갭 명명 컨벤션 (#7)

financial-data-platform 의 `POST /api/meta/data-gaps` 에 macro-scanner 가 기록하는 갭 페이로드의 명명 규약. 같은 갭이 같은 문자열로 누적돼야 `GET /api/meta/data-gaps/summary` 의 topic 별 group by 가 의미를 갖는다 — 자유 텍스트지만 **사실상 enum 처럼** 운영한다.

## 호출 시점

scanner 가 한 항목에 대해 **WebSearch 보강을 사용했고**, 그 데이터가 "fdp 가 차후 수집기를 추가하면 자동으로 채울 수 있을 만한 정기·구조화 데이터" 라고 판단할 때만 기록한다.

기록하지 **않는** 경우:
- 단발성 뉴스/이벤트 (FOMC 결정, OPEC+ 회의, 지정학 사건)
- LLM 의 해석/가공이 본질인 항목 (예: "스마트머니 흐름 평가")
- 이미 fdp 가 커버하는 항목을 단순 추가 컨텍스트 차원에서 WebSearch 한 경우

기록**하는** 경우:
- 정기 발표 시계열인데 fdp 미수집 (예: ICI 주간 ETF flows)
- 외부 차단(Cloudflare/JS 등)으로 LLM 도 못 받은 항목
- capabilities 에 카테고리는 있으나 특정 symbol 이 비어 있는 경우

## 페이로드 스키마

```json
{
  "topic": "<자유 텍스트, 200자 이내>",
  "category": "<enum>",
  "requester": "macro-report:<report_type>",
  "context": "<자유, 보고서 슬러그/주차 등>",
  "reason": "<자유, 한 줄>"
}
```

`topic` 만 필수. 나머지는 권장.

## topic — 같은 갭은 같은 문자열

규칙:
- **영문 소문자** 기본, 고유명사·약어는 원형 유지 (`ICI`, `BTC`, `OPEC+`)
- 명사구. 시제·관사 없음
- 주기성이 있으면 끝에 `weekly` / `monthly` / `quarterly` 부착
- 데이터 종류는 항상 마지막에 단수 명사로 (`flows`, `survey`, `ratio`, `assets`)

### 권장 topic 예시 (category 별)

| category | topic 예시 |
|----------|-----------|
| `liquidity` | `ICI ETF flows weekly` · `primary dealer survey` · `corporate buyback announcements weekly` · `margin debt monthly` · `MMF assets weekly` · `TIPS real yield 5y` · `CME FedWatch probabilities` |
| `insider` | `Form 4 weekly aggregate` · `10b5-1 plan ratio` · `13D 5%+ stake events` · `cluster buying signals` |
| `sector` | `sector ETF flows weekly` · `factor ETF flows weekly` · `creation redemption units` · `thematic ETF flows weekly` |
| `regime` | `S&P 500 vs TLT correlation 60d` · `BTC ETF spot flows` · `cross-asset correlation matrix` |
| `analyst` | `consensus PT revision ratio` · `analyst upgrades downgrades weekly` · `sell-side estimate dispersion` |
| `news` | `FOMC dot plot updates` · `OPEC+ meeting outcomes` |

새 topic 이 필요하면 위 규칙을 따라 만들고, 한 번 정해진 표기는 그대로 재사용.

## category — enum 운영

| 값 | 매칭 report_type | 비고 |
|----|------------------|----|
| `liquidity` | liquidity | |
| `insider` | insider | |
| `sector` | sector | |
| `regime` | regime | |
| `analyst` | analyst | |
| `news` | (어디든) | 단발성 시장 이벤트 — 보통 기록 안 함 |

scanner 의 `report_type` 과 1:1 매칭. 단 한 보고서가 다른 카테고리 갭을 발견할 수 있다 (예: regime scanner 가 ETF flows 갭 발견 → `category=sector`). report_type 강제 매칭이 아닌 **갭의 본질** 기준.

## requester — 형식 고정

```
"macro-report:<report_type>"
```

예: `"macro-report:liquidity"`, `"macro-report:insider"`. report_type 은 scanner 입력 그대로. 다른 형식 금지 — `/summary` 의 requester 필터가 깨진다.

## context — 자유 텍스트

권장: `"YYYY-MM-DD <주기>"` (예: `"2026-04-27 weekly"`). 보고서 슬러그를 적어도 무방. 리뷰 시 "언제 누가 기록했나" 정도만 알 수 있으면 됨.

## reason — 한 줄, 사실 위주

좋은 예:
- `"etf.com Cloudflare 차단으로 fdp 미수집"`
- `"fdp capabilities 에 ICI 항목 없음"`
- `"/api/indicators/M2SL 에 최근 3주 데이터 누락"`

피할 예:
- `"중요한 데이터"` (정보 0)
- `"수집기 만들어주세요"` (요청은 갭 자체로 표현)

## 누적 리뷰 (운영자 메모)

`GET /api/meta/data-gaps/summary` 의 `by_topic[].total` 이 5 이상이고 `open=total` 이면 그 topic 은 수집기 도입 1순위 후보. fdp 측에서 수집기를 도입했으면 `PATCH /api/meta/data-gaps/{id}` 로 `resolved=true` + `resolved_note="#NN <수집기명> 도입"` 마킹.

## 관련

- claude-bridge [#7](https://git.xhhan.com/xhh/claude-bridge/issues/7) — 본 작업 (data_gaps 짝꿍 활성화)
- financial-data-platform [#15](https://git.xhhan.com/xhh/financial-data-platform/issues/15) — fdp 측 구현 (Closed)
- financial-data-platform [#62](https://git.xhhan.com/xhh/financial-data-platform/issues/62) — capabilities 짝꿍 (Closed)
- [token-savings.md](token-savings.md) — 토큰 절감 측정 페어 (data_gaps 누적과 함께 진행)
