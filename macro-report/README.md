# macro-report

거시경제 종합 투자분석 보고서 자동화 플러그인

## 개요

5개 개별 분석 보고서(유동성, 크로스에셋, 내부자 매매, 애널리스트 목표가, 시장 주도 업종)를 수집·작성하고, 이를 종합한 투자 판단 보고서를 생성합니다. 마지막으로 전체의 **쉬운말 버전**을 만들어 금융 용어 없이도 읽을 수 있게 합니다.

## 아키텍처

4단계 파이프라인으로 토큰 효율성을 극대화합니다:

```
[1단계] macro-scanner (Sonnet) × 5 병렬
  ├── 열린 스캔: 최근 2주 핵심 이벤트/서프라이즈
  ├── 이전 보고서 로드 → 베이스라인 + 변경분 식별
  ├── (B 모드) financial-data-platform capabilities 우선 → API 호출
  └── 매칭 안 된 항목만 WebSearch fallback → 구조화된 데이터 수집

[2단계] macro-writer (Opus) × 5 병렬
  └── 수집 데이터 → 개별 보고서 작성·저장

[3단계] macro-writer (Opus) × 1
  └── 5개 보고서 읽기 → 종합보고서 작성

[4단계] macro-writer (Opus) × 6 병렬   ※ --no-plain 으로 생략 가능
  └── 6개 보고서 → 쉬운말 버전 작성 + 원본에 역링크 삽입
```

### 쉬운말 버전 (평이판)

원본 보고서는 전문 용어로 압축돼 있어 금융 배경이 없으면 읽기 어렵습니다. 4단계는 같은 내용을 용어를 풀어 다시 쓴 문서를 원본 옆에 생성합니다.

| 항목 | 내용 |
|------|------|
| 파일명 | 원본 + ` 쉬운 설명` (종합만 `종합 분석 쉬운 설명` 으로 축약) |
| 분량 | 종합 원본의 40~60%, 개별 원본의 30~45% |
| 용어 처리 | `쉬운 말(원어)` 병기 — 예: 시장에 실제로 도는 돈(순유동성) |
| 숫자 | 한국어 단위 변환 — `−$69.1B` → 691억 달러 (주가·목표가는 달러 유지) |
| 차트 | Plotly 재생성 없이 마크다운 표·불릿으로 대체 |
| 원칙 | 결론만 있는 곳에 인과 추가, 독자 의문은 콜아웃으로 선점 |
| 금지 | 원본에 없는 종목·수치·판단 추가, 원본과 다른 결론 (**번역이지 분석이 아님**) |

작성 규칙과 용어 사전의 단일 출처: [plain-language-guide.md](skills/macro-report-workflow/references/plain-language-guide.md)

### 데이터 수집 경로 (B 모드, 시범 전환 중)

`liquidity` 보고서에 한해 macro-scanner 가 `https://stock.xhhan.com/api/meta/capabilities` 를 먼저 fetch 해 사용 가능한 데이터를 동적으로 파악한 뒤, 매칭되는 항목은 financial-data-platform API 를 통해 받고 못 하는 항목만 WebSearch fallback. **사전 매핑은 두지 않고** capabilities 응답이 매번 결정한다 (새 엔드포인트 추가 시 자동 인지).

토글 / 환경변수:

| 항목 | 값 | 용도 |
|------|----|----|
| `--no-api` 인자 | flag | B 모드를 끄고 기존 WebSearch-only(A 모드)로 강제 |
| `MACRO_SKIP_API` env | `1` | 동일 |
| `--api-base=URL` 인자 | URL | financial-data-platform 베이스 URL 오버라이드 (로컬/Tailscale 등) |
| `FDP_API_BASE` env | URL | 동일 |
| `FDP_API_KEY` env | `irp_…` | write 스코프 키. 설정 시 scanner 가 WebSearch 보강한 갭을 `POST /api/meta/data-gaps` 로 자동 누적. 미설정/실패 시 graceful skip — 보고서 생성 영향 없음 |
| `--no-plain` 인자 | flag | 4단계(쉬운말 버전 생성)를 건너뜀 |
| `MACRO_SKIP_PLAIN` env | `1` | 동일 |

토큰 절감 측정 양식: [skills/macro-report-workflow/references/token-savings.md](skills/macro-report-workflow/references/token-savings.md).
데이터 갭 명명 규약: [skills/macro-report-workflow/references/data-gaps-conventions.md](skills/macro-report-workflow/references/data-gaps-conventions.md).

## 커맨드

| 커맨드 | 용도 | 사용법 |
|--------|------|--------|
| `generate` | 5개 보고서 + 종합 + 쉬운말 6개 생성 | `/macro-report:generate [output-path]` |
| `report` | 개별 보고서 1개 생성 (+ 쉬운말) | `/macro-report:report [type] [output-path]` |
| `synthesize` | 기존 5개로 종합보고서만 생성 (+ 쉬운말) | `/macro-report:synthesize [date] [output-path]` |
| `plain` | 기존 보고서의 쉬운말 버전만 생성 | `/macro-report:plain [type\|all] [date] [output-path]` |

### report type

| type | 보고서 |
|------|--------|
| `insider` | 내부자 매매 동향 |
| `analyst` | 애널리스트 목표가 변동 |
| `sector` | 시장 주도 업종 분석 |
| `liquidity` | 유동성 환경 분석 |
| `regime` | 크로스에셋 레짐 분석 |

## 에이전트

| 에이전트 | 모델 | 역할 |
|----------|------|------|
| `macro-scanner` | Sonnet | 열린 스캔 + 데이터 수집 (판단 없음) |
| `macro-writer` | Opus | 분석 + 보고서 작성 (`individual` / `comprehensive` / `plain` 3개 모드) |

## 출력 경로

기본 출력 경로: `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/`

파일명 형식:

| 구분 | 형식 |
|------|------|
| 개별 보고서 | `YYYY-MM-DD [보고서명].md` |
| 종합 보고서 | `YYYY-MM-DD 종합 분석 및 투자 판단.md` |
| 쉬운말 (개별) | `YYYY-MM-DD [보고서명] 쉬운 설명.md` |
| 쉬운말 (종합) | `YYYY-MM-DD 종합 분석 쉬운 설명.md` |

`generate` 1회 실행 시 총 12개 파일이 생성됩니다 (원본 6 + 쉬운말 6). `--no-plain` 사용 시 6개.

## Version History

- **1.6.0** (2026-07-27): 쉬운말 버전(평이판) 생성 기능 추가 — `macro-writer` 에 `plain` 모드 신설, `generate`/`report`/`synthesize` 에 자동 생성 단계 추가, 소급 적용용 `/macro-report:plain` 커맨드 신설, 작성 규칙·용어 사전 단일 출처 [plain-language-guide.md](skills/macro-report-workflow/references/plain-language-guide.md) 추가. `--no-plain` / `MACRO_SKIP_PLAIN=1` 로 비활성화 가능.
- **1.5.1** (2026-04-27): Step 1.5 의 data_gaps POST 가 Windows mingw-bash 에서 한글 페이로드 cp949 트랜스코딩으로 100% 실패하던 결함 수정 — `--data "$line"` → 임시파일 + `--data-binary @file` 패턴. [#5](https://github.com/elhaz/claude-plugin/issues/5).
- **1.5.0** (2026-04-27): data_gaps 짝꿍 활성화 — scanner sidecar JSONL + command Bash POST 훅, `FDP_API_KEY` 환경변수, [data-gaps-conventions.md](skills/macro-report-workflow/references/data-gaps-conventions.md) 추가. [claude-bridge #7](https://git.xhhan.com/xhh/claude-bridge/issues/7).
- **1.4.0** (2026-04-26): financial-data-platform capabilities 우선 경로 시범 도입 (`liquidity` 한정, A/B 토글). [issue #6](https://git.xhhan.com/xhh/financial-data-platform/issues/6).
- **1.3.0** (2026-04-25): 토큰 최적화 — 파일 기반 핸드오프, 경로 참조, 요약 우선 읽기.
- **1.0.0** (2026-03-29): 초기 릴리즈. 3단계 파이프라인, 병렬 에이전트 구조
