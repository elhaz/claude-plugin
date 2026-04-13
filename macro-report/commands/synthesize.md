---
name: synthesize
description: 기존 5개 개별 보고서를 기반으로 종합 투자판단 보고서만 생성합니다
argument-hint: "[date] [output-path]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
---

# /macro-report:synthesize

이미 작성된 5개 개별 보고서를 읽어 종합 투자판단 보고서만 생성한다. 웹 검색 없이 기존 보고서만 활용.

## Arguments

- **date** (선택): 대상 보고서 날짜 (YYYY-MM-DD). 기본값: 오늘
- **output-path** (선택): 저장 경로. 기본값: `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/`

## 실행 순서

### Step 0: 5개 보고서 탐색

지정된 date로 5개 보고서를 Glob으로 탐색:

```
[output-path]/[date] 내부자 매매 동향.md
[output-path]/[date] 애널리스트 목표가 변동.md
[output-path]/[date] 시장 주도 업종 분석.md
[output-path]/[date] 유동성 환경 분석.md
[output-path]/[date] 크로스에셋 레짐 분석.md
```

5개 중 누락된 문서가 있으면 사용자에게 알리고 확인 요청.

### Step 1: 종합보고서 작성 (macro-writer × 1)

```
Agent(macro-writer):
  - mode: comprehensive
  - report_paths: Step 0에서 확인된 5개 경로
  - comprehensive_template_path: references/comprehensive-template.md 경로
  - scoring_criteria_path: references/scoring-criteria.md 경로
  - previous_comprehensive_path: 이전 종합보고서 (있으면)
  - output_path: [output-path]/[date] 종합 분석 및 투자 판단.md
  - report_date: [date]
```

> [!important] 요약 우선 + 전문 후속 Read
> 종합 Writer는 5개 보고서의 `## 종합보고서용 요약` 섹션을 먼저 Read하여 전체 구조를 파악한 뒤,
> 5개 보고서 전문을 순차적으로 Read한다. 한꺼번에 읽지 않아 컨텍스트 효율이 높다.

### Step 2: 완료 보고

생성된 종합보고서 경로와 핵심 판단 요약을 사용자에게 보고.

## 사용 예시

```
/macro-report:synthesize
/macro-report:synthesize 2026-03-29
/macro-report:synthesize 2026-03-29 02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/
```
