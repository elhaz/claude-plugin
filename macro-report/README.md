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
  └── 항목별 웹 검색 → 구조화된 데이터 수집

[2단계] macro-writer (Opus) × 5 병렬
  └── 수집 데이터 → 개별 보고서 작성·저장

[3단계] macro-writer (Opus) × 1
  └── 5개 보고서 읽기 → 종합보고서 작성
```

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

- **1.0.0** (2026-03-29): 초기 릴리즈. 3단계 파이프라인, 병렬 에이전트 구조
