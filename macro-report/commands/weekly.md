---
name: weekly
description: 거시경제 주간 보고 2부 — 데이터 파일로 판단 파일(예측 원장) 작성 → 검증·채점 → 거시경제 주간 보고(쉬운말) 작성
argument-hint: "[YYYY-MM-DD] [--api-base=URL]"
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Agent
---

# /macro-report:weekly

1부(`/macro-report:collect`)가 남긴 데이터 파일로 판단하고, 사람이 읽는 **거시경제 주간 보고** 한 개를 만든다.

산출물:

| 파일 | 용도 |
|---|---|
| `분석/데이터/{날짜}/판단.md` | LLM 용 판단 + **예측 원장** (```json). 게시 후 수정 금지 |
| `분석/데이터/{날짜}/채점.md` | 지난 예측 성적 + 차트 2개 (스크립트 생성) |
| `분석/{날짜} 거시경제 주간 보고.md` | 사람이 읽는 유일한 문서 (공개 게시 대상) |

## Arguments

- **YYYY-MM-DD** (선택): 판단일. 기본 오늘. 1부와 같은 날짜여야 한다
- **--api-base=URL**: 채점용 데이터 플랫폼 주소 (기본 `FDP_API_BASE` → `http://localhost:8000` → 공개 주소 순으로 자동 선택)

## Step 0: 준비 (Bash 한 번)

```bash
DATE_ARG=$(printf ' %s ' $ARGUMENTS | grep -oE ' [0-9]{4}-[0-9]{2}-[0-9]{2} ' | tr -d ' ' | head -1)
TODAY="${DATE_ARG:-$(date '+%Y-%m-%d')}"
OUT="${OBSIDIAN_VAULT:-.}/02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석"
DATA="$OUT/데이터/$TODAY"
P="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/elhaz-plugins/macro-report/*/ | sort -V | tail -1)}"
P="${P%/}"
PREV=$(for d in "$OUT/데이터"/????-??-??/; do [ -d "$d" ] && basename "$d"; done | awk -v t="$TODAY" '$0 < t' | sort | tail -1)
API_ARG=""; for tok in $ARGUMENTS; do case "$tok" in --api-base=*) API_ARG="--api-base ${tok#--api-base=}" ;; esac; done
n=0; for t in liquidity regime sector insider outlook; do [ -s "$DATA/$t.md" ] && n=$((n+1)) || echo "누락 $t"; done
echo "TODAY=$TODAY PREV=${PREV:-없음} 데이터 $n/5 P=$P"
```

**데이터 파일이 3개 미만이면 중단**하고 `데이터 파일 n/5 — 판단 불가` 를 보고한다. 1부를 다시 돌려야 한다.

## Step 1: 판단 + 보고서 (macro-writer × 1)

```
Agent(macro-writer):
  - data_dir: $DATA
  - previous_judgment_path: $OUT/데이터/$PREV/판단.md   (PREV 가 있을 때)
  - previous_report_path: $OUT/$PREV 거시경제 주간 보고.md   (있을 때)
  - judgment_path: $DATA/판단.md
  - report_path: $OUT/$TODAY 거시경제 주간 보고.md
  - references_dir: $P/skills/macro-report-workflow/references
  - score_command:
      validate: python3 "$P/scripts/weekly_score.py" validate "$DATA/판단.md"
      score:    python3 "$P/scripts/weekly_score.py" score --data-root "$OUT/데이터" --date $TODAY $API_ARG
  - report_date: $TODAY
```

경로는 Step 0 에서 확정한 **실제 값으로 치환해서** 넘긴다 (에이전트는 셸 변수를 모른다).

Agent 타입 `macro-report:macro-writer` 가 없으면 `$P/agents/macro-writer.md` 본문을 `general-purpose` 에이전트 프롬프트에 넣어 같은 입력으로 호출한다.

## Step 2: 확인 (Bash)

```bash
python3 "$P/scripts/weekly_score.py" validate "$DATA/판단.md"
R="$OUT/$TODAY 거시경제 주간 보고.md"
[ -s "$R" ] && echo "보고서 OK" || echo "보고서 없음"
[ -s "$DATA/채점.md" ] && echo "채점 OK" || echo "채점 없음"
echo "250자 넘는 줄: $(awk 'length($0) > 250 && !/^\|/ && !/^\[\^/ && !/^ *[{}"\[\]]/' "$R" | wc -l)"
echo "plotly 블록: $(grep -c '^```plotly' "$R")"
```

- 검증 실패 또는 보고서 없음 → writer 를 **한 번만** 다시 호출 (같은 입력 + 실패 내용)
- 250자 넘는 줄·plotly 블록 수(2 기대)는 보고에만 적는다

## Step 3: 완료 보고

세 줄: 보고서 경로, 한 줄 요약(writer 보고), 확인 결과.
