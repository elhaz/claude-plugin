---
name: report
description: 개별 거시경제 분석 보고서 1개를 생성합니다
argument-hint: "[type] [output-path]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
---

# /macro-report:report

5개 보고서 유형 중 1개를 선택하여 개별 분석 보고서를 생성한다.

## Arguments

- **type** (필수): `insider` | `analyst` | `sector` | `liquidity` | `regime`
- **output-path** (선택): 저장 경로. 기본값: `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/`

### type 매핑

| type | 보고서명 | 질문 템플릿 |
|------|---------|-----------|
| `insider` | 내부자 매매 동향 | question-insider.md |
| `analyst` | 애널리스트 목표가 변동 | question-analyst.md |
| `sector` | 시장 주도 업종 분석 | question-sector.md |
| `liquidity` | 유동성 환경 분석 | question-liquidity.md |
| `regime` | 크로스에셋 레짐 분석 | question-regime.md |

## 실행 순서

### Step 0: 사전 준비

1. 오늘 날짜 → `report_date`
2. 해당 type의 이전 보고서 탐색 (Glob)
3. 질문 템플릿 로드

### Step 1: 데이터 수집 (macro-scanner × 1)

```
Agent(macro-scanner):
  - report_type: [type]
  - previous_report_path: 이전 보고서 (있으면)
  - question_template: 질문 템플릿
```

### Step 2: 보고서 작성 (macro-writer × 1)

```
Agent(macro-writer):
  - mode: individual
  - report_type: [type]
  - collected_data: Step 1 반환 데이터
  - previous_report_path: 이전 보고서
  - output_path: [output-path]/[report_date] [보고서명].md
  - question_template: 질문 템플릿
  - report_date: 오늘 날짜
```

### Step 3: 완료 보고

생성된 파일 경로와 핵심 요약을 사용자에게 보고.

## 사용 예시

```
/macro-report:report insider
/macro-report:report liquidity
/macro-report:report regime 03_Resources/기술문서/
```
