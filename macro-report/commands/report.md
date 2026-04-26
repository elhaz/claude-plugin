---
name: report
description: 개별 거시경제 분석 보고서 1개를 생성합니다
argument-hint: "[type] [output-path] [--no-api] [--api-base=URL]"
allowed-tools:
  - Bash
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
- **--no-api** (선택 플래그): financial-data-platform 우선 경로를 끄고 기존 WebSearch-only 경로(A 모드)로 강제. 환경변수 `MACRO_SKIP_API=1` 과 동등.
- **--api-base=URL** (선택): financial-data-platform 베이스 URL 오버라이드. 우선순위는 `--api-base 인자 > $FDP_API_BASE > https://stock.xhhan.com`.

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
3. `[output-path]/.scan/` 디렉토리 확인 (없으면 생성)
4. **데이터 수집 모드 결정** (Bash 한 번):

```bash
# --no-api 플래그 또는 MACRO_SKIP_API=1 이면 use_api=false
# --api-base=URL 또는 $FDP_API_BASE 가 있으면 그 값을 사용, 없으면 기본 prod URL
# $ARGUMENTS 안의 토큰들을 점검
USE_API=true
API_BASE="${FDP_API_BASE:-https://stock.xhhan.com}"
[ "${MACRO_SKIP_API:-0}" = "1" ] && USE_API=false
case " $ARGUMENTS " in
  *" --no-api "*) USE_API=false ;;
esac
for tok in $ARGUMENTS; do
  case "$tok" in --api-base=*) API_BASE="${tok#--api-base=}" ;; esac
done
echo "use_api=$USE_API"
echo "api_base_url=$API_BASE"
```

> [!note] 질문 템플릿은 로드하지 않음
> Scanner가 직접 Read하므로 오케스트레이터에서 읽을 필요가 없다.

### Step 1: 데이터 수집 (macro-scanner × 1)

```
Agent(macro-scanner):
  - report_type: [type]
  - previous_report_path: 이전 보고서 (있으면)
  - question_template_path: 질문 템플릿 파일 경로
  - scan_data_path: [output-path]/.scan/[type]_[report_date].md
  - use_api: Step 0에서 결정된 값
  - api_base_url: Step 0에서 결정된 값
```

Scanner는 수집 데이터를 scan_data_path에 Write하고 경로만 보고한다.

### Step 2: 보고서 작성 (macro-writer × 1)

```
Agent(macro-writer):
  - mode: individual
  - report_type: [type]
  - scan_data_path: Step 1에서 저장된 파일 경로
  - previous_report_path: 이전 보고서
  - output_path: [output-path]/[report_date] [보고서명].md
  - question_template_path: 질문 템플릿 파일 경로
  - report_date: 오늘 날짜
```

### Step 3: 완료 보고

생성된 파일 경로와 핵심 요약을 사용자에게 보고. 보고 말미에 사용된 모드(A/B)와 capabilities_used 플래그를 한 줄 명시 (scan_data 의 `## 수집 메타` 섹션에서 발췌).

## 사용 예시

```
/macro-report:report insider
/macro-report:report liquidity
/macro-report:report liquidity --no-api
/macro-report:report liquidity --api-base=http://localhost:8000
/macro-report:report regime 03_Resources/기술문서/
```
