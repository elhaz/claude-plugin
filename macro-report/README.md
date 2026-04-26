# macro-report

거시경제 종합 투자분석 보고서 자동화 플러그인

## 개요

5개 개별 분석 보고서(유동성, 크로스에셋, 내부자 매매, 애널리스트 목표가, 시장 주도 업종)를 수집·작성하고, 이를 종합한 투자 판단 보고서를 생성합니다.

## 아키텍처

3단계 파이프라인으로 토큰 효율성을 극대화합니다:

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
```

### 데이터 수집 경로 (B 모드, 시범 전환 중)

`liquidity` 보고서에 한해 macro-scanner 가 `https://stock.xhhan.com/api/meta/capabilities` 를 먼저 fetch 해 사용 가능한 데이터를 동적으로 파악한 뒤, 매칭되는 항목은 financial-data-platform API 를 통해 받고 못 하는 항목만 WebSearch fallback. **사전 매핑은 두지 않고** capabilities 응답이 매번 결정한다 (새 엔드포인트 추가 시 자동 인지).

토글 / 환경변수:

| 항목 | 값 | 용도 |
|------|----|----|
| `--no-api` 인자 | flag | B 모드를 끄고 기존 WebSearch-only(A 모드)로 강제 |
| `MACRO_SKIP_API` env | `1` | 동일 |
| `--api-base=URL` 인자 | URL | financial-data-platform 베이스 URL 오버라이드 (로컬/Tailscale 등) |
| `FDP_API_BASE` env | URL | 동일 |

토큰 절감 측정 양식: [skills/macro-report-workflow/references/token-savings.md](skills/macro-report-workflow/references/token-savings.md).

## 커맨드

| 커맨드 | 용도 | 사용법 |
|--------|------|--------|
| `generate` | 5개 보고서 + 종합 전체 생성 | `/macro-report:generate [output-path]` |
| `report` | 개별 보고서 1개 생성 | `/macro-report:report [type] [output-path]` |
| `synthesize` | 기존 5개로 종합보고서만 생성 | `/macro-report:synthesize [date] [output-path]` |

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
| `macro-writer` | Opus | 분석 + 보고서 작성 |

## 출력 경로

기본 출력 경로: `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/`

파일명 형식: `YYYY-MM-DD [보고서명].md`

## Version History

- **1.4.0** (2026-04-26): financial-data-platform capabilities 우선 경로 시범 도입 (`liquidity` 한정, A/B 토글). [issue #6](https://git.xhhan.com/xhh/financial-data-platform/issues/6).
- **1.3.0** (2026-04-25): 토큰 최적화 — 파일 기반 핸드오프, 경로 참조, 요약 우선 읽기.
- **1.0.0** (2026-03-29): 초기 릴리즈. 3단계 파이프라인, 병렬 에이전트 구조
