---
name: generate
description: 5개 거시경제 분석 보고서 + 종합 투자판단 보고서를 일괄 생성합니다
argument-hint: "[output-path]"
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

# /macro-report:generate

5개 개별 보고서(내부자 매매, 애널리스트 목표가, 시장 주도 업종, 유동성 환경, 크로스에셋 레짐)를 병렬 수집·작성하고, 종합 투자판단 보고서를 생성한다.

## Arguments

- **output-path** (선택): 보고서 저장 디렉토리. 기본값: `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/`

## 실행 순서

### Step 0: 사전 준비

1. 오늘 날짜 확인 → `report_date` 설정
2. output-path 디렉토리 존재 확인
3. 이전 보고서 탐색: 각 유형별 가장 최근 보고서 경로 파악
   ```
   Glob: [output-path]/*내부자 매매 동향.md → 최신 1개
   Glob: [output-path]/*애널리스트 목표가 변동.md → 최신 1개
   Glob: [output-path]/*시장 주도 업종 분석.md → 최신 1개
   Glob: [output-path]/*유동성 환경 분석.md → 최신 1개
   Glob: [output-path]/*크로스에셋 레짐 분석.md → 최신 1개
   ```
4. 질문 템플릿 5개 로드 (skills/macro-report-workflow/references/question-*.md)

### Step 1: 데이터 수집 (macro-scanner × 5, 병렬)

5개 보고서 유형에 대해 **동시에** macro-scanner 에이전트를 호출한다:

```
Agent(macro-scanner) × 5 병렬:
  각각에 전달:
  - report_type: insider / analyst / sector / liquidity / regime
  - previous_report_path: Step 0에서 찾은 이전 보고서
  - question_template: 해당 유형의 질문 템플릿
```

> [!important] 병렬 실행
> 5개 에이전트를 **하나의 메시지에서 동시에** 호출한다. 각 에이전트는 독립 컨텍스트에서 실행되므로 토큰 누적이 발생하지 않는다.

각 에이전트는 구조화된 데이터를 반환한다.

### Step 2: 보고서 작성 (macro-writer × 5, 병렬)

5개 수집 결과에 대해 **동시에** macro-writer 에이전트를 호출한다:

```
Agent(macro-writer) × 5 병렬:
  각각에 전달:
  - mode: individual
  - report_type: insider / analyst / sector / liquidity / regime
  - collected_data: Step 1에서 반환된 데이터
  - previous_report_path: 이전 보고서
  - output_path: [output-path]/[report_date] [보고서명].md
  - question_template: 질문 템플릿
  - report_date: 오늘 날짜
```

**파일명 매핑:**

| type | 파일명 |
|------|--------|
| insider | `YYYY-MM-DD 내부자 매매 동향.md` |
| analyst | `YYYY-MM-DD 애널리스트 목표가 변동.md` |
| sector | `YYYY-MM-DD 시장 주도 업종 분석.md` |
| liquidity | `YYYY-MM-DD 유동성 환경 분석.md` |
| regime | `YYYY-MM-DD 크로스에셋 레짐 분석.md` |

### Step 3: 종합보고서 작성 (macro-writer × 1)

5개 보고서가 모두 저장된 후, macro-writer를 종합 모드로 호출한다:

```
Agent(macro-writer):
  - mode: comprehensive
  - report_paths: Step 2에서 저장된 5개 파일 경로
  - comprehensive_template: references/comprehensive-template.md 로드
  - previous_comprehensive_path: 이전 종합보고서 (있으면)
  - output_path: [output-path]/[report_date] 종합 분석 및 투자 판단.md
  - report_date: 오늘 날짜
```

### Step 4: 완료 보고

생성된 6개 파일 경로와 각 보고서의 핵심 요약 1줄을 사용자에게 보고한다.

## 에러 처리

- Step 1에서 특정 scanner가 실패해도 나머지는 계속 진행
- 실패한 보고서는 `[생성 실패: 사유]`로 표기하고, 종합보고서에서 해당 섹션은 "데이터 미수집"으로 처리
- 5개 중 3개 이상 실패하면 종합보고서 생성을 중단하고 사용자에게 보고

## 사용 예시

```
/macro-report:generate
/macro-report:generate 02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/
```
