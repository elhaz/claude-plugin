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
- **`FDP_API_KEY` env** (선택): write 스코프 키. 설정되어 있으면 Step 1 종료 후 scanner 가 누적한 데이터 갭을 `POST /api/meta/data-gaps` 로 전송. 미설정/실패 시 graceful skip — 보고서 생성에는 영향 없음.

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

Scanner는 수집 데이터를 scan_data_path에 Write하고 경로만 보고한다. 데이터 갭이 누적된 경우 sidecar `${scan_data_path%.md}_data_gaps.jsonl` 도 함께 생성한다.

### Step 1.5: 데이터 갭 전송 (선택, graceful)

Step 1 직후, sidecar JSONL 이 존재하고 `FDP_API_KEY` 가 설정되어 있으면 한 줄씩 fdp 에 POST. 실패는 모두 무시 (보고서 생성 차단 금지).

> [!important] Windows mingw-bash 의 cp949 트랜스코딩 우회
> `curl --data "$line"` 은 Windows mingw-bash 에서 한글 페이로드를 cp949 로 변환해 fdp 가 invalid UTF-8 → HTTP 400 으로 거부 ([#5](https://github.com/elhaz/claude-plugin/issues/5)).
> 한 줄을 임시파일에 `printf` 로 쓰고 `--data-binary @file` 로 보내야 UTF-8 보존.

```bash
# 오케스트레이터가 다음을 채워 호출:
#   SCAN_DATA_PATH = Step 1 의 scan_data_path
# Step 0 의 USE_API/API_BASE 값을 동일 규칙으로 재유도 (셸 상태는 호출 간 비휘발).
USE_API=true
API_BASE="${FDP_API_BASE:-https://stock.xhhan.com}"
[ "${MACRO_SKIP_API:-0}" = "1" ] && USE_API=false
case " $ARGUMENTS " in *" --no-api "*) USE_API=false ;; esac
for tok in $ARGUMENTS; do
  case "$tok" in --api-base=*) API_BASE="${tok#--api-base=}" ;; esac
done

GAPS_FILE="${SCAN_DATA_PATH%.md}_data_gaps.jsonl"
if [ -f "$GAPS_FILE" ] && [ -n "${FDP_API_KEY:-}" ] && [ "$USE_API" = "true" ]; then
  TMP_GAP="${TMPDIR:-/tmp}/_macro_gap_$$.json"
  trap 'rm -f "$TMP_GAP"' EXIT
  posted=0; failed=0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    printf '%s' "$line" > "$TMP_GAP"
    if curl -fsS -m 5 -X POST "$API_BASE/api/meta/data-gaps" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $FDP_API_KEY" \
        --data-binary @"$TMP_GAP" >/dev/null 2>&1; then
      posted=$((posted+1))
    else
      failed=$((failed+1))
    fi
  done < "$GAPS_FILE"
  echo "data_gaps: posted=$posted failed=$failed"
elif [ -f "$GAPS_FILE" ]; then
  echo "data_gaps: skipped (FDP_API_KEY 부재 또는 USE_API=false)"
fi
```

> 명명 규약은 `skills/macro-report-workflow/references/data-gaps-conventions.md` 단일 출처.

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
