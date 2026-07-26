---
name: generate
description: 5개 거시경제 분석 보고서 + 종합 투자판단 보고서 + 쉬운말 버전 6개를 일괄 생성합니다
argument-hint: "[output-path] [--no-api] [--no-plain] [--api-base=URL]"
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

# /macro-report:generate

5개 개별 보고서(내부자 매매, 애널리스트 목표가, 시장 주도 업종, 유동성 환경, 크로스에셋 레짐)를 병렬 수집·작성하고, 종합 투자판단 보고서를 생성한 뒤, 6개 전부의 **쉬운말 버전**을 병렬 생성한다.

## Arguments

- **output-path** (선택): 보고서 저장 디렉토리. 기본값: `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/`
- **--no-api** (선택 플래그): 모든 scanner 에 `use_api=false` 전파. 환경변수 `MACRO_SKIP_API=1` 과 동등.
- **--no-plain** (선택 플래그): Step 4(쉬운말 버전 생성)를 건너뛴다. 환경변수 `MACRO_SKIP_PLAIN=1` 과 동등. 쉬운말 6개는 원본 대비 약 40~60% 분량이므로 토큰을 아껴야 할 때 사용.
- **--api-base=URL** (선택): financial-data-platform 베이스 URL 오버라이드. 우선순위는 `--api-base 인자 > $FDP_API_BASE > https://stock.xhhan.com`.
- **`FDP_API_KEY` env** (선택): write 스코프 키. 설정되어 있으면 Step 1 종료 후 5개 scanner 의 sidecar JSONL 을 `POST /api/meta/data-gaps` 로 전송. 미설정/실패 시 graceful skip — 보고서 생성에는 영향 없음.

> 5종 중 시범 전환 대상은 현재 `liquidity` 한정. 나머지 4종은 scanner 가 Phase 0 에서 자동 A 모드로 처리되므로 토글은 사실상 liquidity 에만 영향.

## 실행 순서

### Step 0: 사전 준비

1. 오늘 날짜 확인 → `report_date` 설정
2. output-path 디렉토리 존재 확인. `[output-path]/.scan/` 디렉토리도 확인 (없으면 생성)
3. 이전 보고서 탐색: 각 유형별 가장 최근 보고서 경로 파악
   ```
   Glob: [output-path]/*내부자 매매 동향.md → 최신 1개
   Glob: [output-path]/*애널리스트 목표가 변동.md → 최신 1개
   Glob: [output-path]/*시장 주도 업종 분석.md → 최신 1개
   Glob: [output-path]/*유동성 환경 분석.md → 최신 1개
   Glob: [output-path]/*크로스에셋 레짐 분석.md → 최신 1개
   ```
4. **실행 모드 결정** (Bash 한 번, 5개 scanner 와 Step 4 가 공유):

```bash
USE_API=true
USE_PLAIN=true
API_BASE="${FDP_API_BASE:-https://stock.xhhan.com}"
[ "${MACRO_SKIP_API:-0}" = "1" ] && USE_API=false
[ "${MACRO_SKIP_PLAIN:-0}" = "1" ] && USE_PLAIN=false
case " $ARGUMENTS " in
  *" --no-api "*) USE_API=false ;;
esac
case " $ARGUMENTS " in
  *" --no-plain "*) USE_PLAIN=false ;;
esac
for tok in $ARGUMENTS; do
  case "$tok" in --api-base=*) API_BASE="${tok#--api-base=}" ;; esac
done
echo "use_api=$USE_API"
echo "use_plain=$USE_PLAIN"
echo "api_base_url=$API_BASE"
```

> [!note] 질문 템플릿은 로드하지 않음
> Scanner가 직접 Read하므로 오케스트레이터에서 질문 템플릿을 읽을 필요가 없다.

### Step 1: 데이터 수집 (macro-scanner × 5, 병렬)

5개 보고서 유형에 대해 **동시에** macro-scanner 에이전트를 호출한다:

```
Agent(macro-scanner) × 5 병렬:
  각각에 전달:
  - report_type: insider / analyst / sector / liquidity / regime
  - previous_report_path: Step 0에서 찾은 이전 보고서
  - question_template_path: 질문 템플릿 파일 경로
  - scan_data_path: [output-path]/.scan/[report_type]_[report_date].md
  - use_api: Step 0에서 결정된 값
  - api_base_url: Step 0에서 결정된 값
```

> [!important] 병렬 실행 + 파일 기반 핸드오프
> 5개 에이전트를 **하나의 메시지에서 동시에** 호출한다. 각 에이전트는 독립 컨텍스트에서 실행되므로 토큰 누적이 발생하지 않는다.
> 각 에이전트는 수집 데이터를 **scan_data_path에 Write**하고, **저장 경로만 보고**한다. 오케스트레이터는 수집 데이터 전문을 수신하지 않는다.
> 데이터 갭이 누적된 경우 sidecar `${scan_data_path%.md}_data_gaps.jsonl` 도 함께 생성된다 (Step 1.5 가 일괄 POST).

### Step 1.5: 데이터 갭 전송 (선택, graceful)

5개 scanner 가 모두 종료된 후, 존재하는 sidecar JSONL 들을 모아 한 줄씩 fdp 에 POST. `FDP_API_KEY` 미설정 또는 `USE_API=false` 면 전체 skip. 실패는 모두 무시 (보고서 생성 차단 금지).

> [!important] Windows mingw-bash 의 cp949 트랜스코딩 우회
> `curl --data "$line"` 은 Windows mingw-bash 에서 한글 페이로드를 cp949 로 변환해 fdp 가 invalid UTF-8 → HTTP 400 으로 거부 ([#5](https://github.com/elhaz/claude-plugin/issues/5)).
> 한 줄을 임시파일에 `printf` 로 쓰고 `--data-binary @file` 로 보내야 UTF-8 보존.

```bash
# 오케스트레이터가 다음을 채워 호출:
#   OUTPUT_PATH   = Step 0 의 output-path (scan 디렉토리의 부모)
#   REPORT_DATE   = Step 0 의 report_date (YYYY-MM-DD)
# Step 0 의 USE_API/API_BASE 값을 동일 규칙으로 재유도 (셸 상태는 호출 간 비휘발).
USE_API=true
API_BASE="${FDP_API_BASE:-https://stock.xhhan.com}"
[ "${MACRO_SKIP_API:-0}" = "1" ] && USE_API=false
case " $ARGUMENTS " in *" --no-api "*) USE_API=false ;; esac
for tok in $ARGUMENTS; do
  case "$tok" in --api-base=*) API_BASE="${tok#--api-base=}" ;; esac
done

if [ -n "${FDP_API_KEY:-}" ] && [ "$USE_API" = "true" ]; then
  TMP_GAP="${TMPDIR:-/tmp}/_macro_gap_$$.json"
  trap 'rm -f "$TMP_GAP"' EXIT
  posted=0; failed=0
  for type in insider analyst sector liquidity regime; do
    GAPS_FILE="${OUTPUT_PATH}/.scan/${type}_${REPORT_DATE}_data_gaps.jsonl"
    [ -f "$GAPS_FILE" ] || continue
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
  done
  echo "data_gaps: posted=$posted failed=$failed"
else
  echo "data_gaps: skipped (FDP_API_KEY 부재 또는 USE_API=false)"
fi
```

> 명명 규약은 `skills/macro-report-workflow/references/data-gaps-conventions.md` 단일 출처.

### Step 2: 보고서 작성 (macro-writer × 5, 병렬)

5개 수집 결과에 대해 **동시에** macro-writer 에이전트를 호출한다:

```
Agent(macro-writer) × 5 병렬:
  각각에 전달:
  - mode: individual
  - report_type: insider / analyst / sector / liquidity / regime
  - scan_data_path: Step 1에서 저장된 파일 경로
  - previous_report_path: 이전 보고서
  - output_path: [output-path]/[report_date] [보고서명].md
  - question_template_path: 질문 템플릿 파일 경로
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
  - comprehensive_template_path: references/comprehensive-template.md 경로
  - scoring_criteria_path: references/scoring-criteria.md 경로
  - previous_comprehensive_path: 이전 종합보고서 (있으면)
  - output_path: [output-path]/[report_date] 종합 분석 및 투자 판단.md
  - report_date: 오늘 날짜
```

> [!important] 요약 우선 + 전문 후속 Read
> 종합 Writer는 5개 보고서의 `## 종합보고서용 요약` 섹션을 먼저 Read하여 전체 구조를 파악한 뒤,
> 5개 보고서 전문을 순차적으로 Read한다. 한꺼번에 읽지 않아 컨텍스트 효율이 높다.

### Step 4: 쉬운말 버전 작성 (macro-writer × 6, 병렬)

> Step 0 에서 `use_plain=false` 로 결정됐으면 이 단계를 통째로 건너뛴다.

6개 보고서(개별 5 + 종합 1)가 모두 저장된 후, **동시에** macro-writer 를 plain 모드로 호출한다:

```
Agent(macro-writer) × 6 병렬:
  각각에 전달:
  - mode: plain
  - report_type: insider / analyst / sector / liquidity / regime / comprehensive
  - source_report_path: Step 2·3에서 저장된 원본 보고서 경로
  - plain_guide_path: references/plain-language-guide.md 경로
  - output_path: [output-path]/[report_date] [보고서명] 쉬운 설명.md
  - report_date: 오늘 날짜
```

**파일명 매핑:**

| type | 원본 | 쉬운말 버전 |
|------|------|------------|
| insider | `YYYY-MM-DD 내부자 매매 동향.md` | `YYYY-MM-DD 내부자 매매 동향 쉬운 설명.md` |
| analyst | `YYYY-MM-DD 애널리스트 목표가 변동.md` | `YYYY-MM-DD 애널리스트 목표가 변동 쉬운 설명.md` |
| sector | `YYYY-MM-DD 시장 주도 업종 분석.md` | `YYYY-MM-DD 시장 주도 업종 분석 쉬운 설명.md` |
| liquidity | `YYYY-MM-DD 유동성 환경 분석.md` | `YYYY-MM-DD 유동성 환경 분석 쉬운 설명.md` |
| regime | `YYYY-MM-DD 크로스에셋 레짐 분석.md` | `YYYY-MM-DD 크로스에셋 레짐 분석 쉬운 설명.md` |
| comprehensive | `YYYY-MM-DD 종합 분석 및 투자 판단.md` | `YYYY-MM-DD 종합 분석 쉬운 설명.md` |

> [!important] 6개 병렬 + 원본 역링크
> 6개 에이전트를 **하나의 메시지에서 동시에** 호출한다. 각 에이전트는 자기 원본 1개만 Read하므로 서로 간섭하지 않는다.
> 각 에이전트는 쉬운말 문서를 Write한 뒤, **원본의 `## 관련문서` 맨 위에 역링크 1줄을 Edit로 삽입**한다. 서로 다른 파일을 편집하므로 병렬 충돌이 없다.
> 작성 규칙의 단일 출처는 `references/plain-language-guide.md` 이며, 오케스트레이터는 이 파일을 읽지 않고 **경로만 전달**한다.

### Step 5: 임시 파일 정리 (선택)

`.scan/` 디렉토리의 임시 파일을 삭제한다.

### Step 6: 완료 보고

생성된 파일 경로와 각 보고서의 핵심 요약 1줄을 사용자에게 보고한다. 쉬운말 버전을 생성한 경우 총 12개(원본 6 + 쉬운말 6), 건너뛴 경우 6개.

## 에러 처리

- Step 1에서 특정 scanner가 실패해도 나머지는 계속 진행
- 실패한 보고서는 `[생성 실패: 사유]`로 표기하고, 종합보고서에서 해당 섹션은 "데이터 미수집"으로 처리
- 5개 중 3개 이상 실패하면 종합보고서 생성을 중단하고 사용자에게 보고
- **Step 4의 개별 실패는 원본 보고서에 영향을 주지 않는다.** 쉬운말 6개 중 일부가 실패해도 나머지는 계속 진행하고, 실패분은 완료 보고에 명시한다. 나중에 `/macro-report:plain` 으로 개별 재생성할 수 있다

## 사용 예시

```
/macro-report:generate
/macro-report:generate 02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/
/macro-report:generate --no-api
/macro-report:generate --no-plain
/macro-report:generate --api-base=http://localhost:8000
```
