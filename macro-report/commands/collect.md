---
name: collect
description: 거시경제 주간 보고 1부 — 뉴스 헤드라인 + 데이터 파일 5종(유동성·레짐·업종·내부자·뉴스전망) 수집
argument-hint: "[YYYY-MM-DD] [--no-api] [--api-base=URL]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Agent
---

# /macro-report:collect

주간 보고의 재료를 모은다. **문장으로 된 보고서는 만들지 않는다** — 결과는 숫자·사실·출처만 담긴 데이터 파일 5개이고, 영구 보관되어 2부(`/macro-report:weekly`)의 유일한 입력이 된다.

## Arguments

- **YYYY-MM-DD** (선택): 판단일. 기본 오늘
- **--no-api**: scanner 에 `use_api=false` (`MACRO_SKIP_API=1` 과 같음)
- **--api-base=URL**: 데이터 플랫폼 공개 주소 (기본 `$FDP_API_BASE` → `https://findata.xhhan.com`). scanner 의 WebFetch 용
- **`FDP_API_KEY` 또는 `FDP_REPORTER_API_KEY` env** (선택): 있으면 scanner 가 남긴 데이터 갭을 `POST /api/meta/data-gaps` 로 전송

## Step 0: 준비 (Bash 한 번)

```bash
DATE_ARG=$(printf ' %s ' $ARGUMENTS | grep -oE ' [0-9]{4}-[0-9]{2}-[0-9]{2} ' | tr -d ' ' | head -1)
TODAY="${DATE_ARG:-$(date '+%Y-%m-%d')}"
OUT="${OBSIDIAN_VAULT:-.}/02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석"
DATA="$OUT/데이터/$TODAY"
P="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/elhaz-plugins/macro-report/*/ | sort -V | tail -1)}"
P="${P%/}"
REF="$P/skills/macro-report-workflow/references"
mkdir -p "$DATA"
# 지난주 데이터 디렉토리 = 오늘보다 앞선 날짜 중 가장 최근
PREV=$(for d in "$OUT/데이터"/????-??-??/; do [ -d "$d" ] && basename "$d"; done | awk -v t="$TODAY" '$0 < t' | sort | tail -1)
USE_API=true; API_BASE="${FDP_API_BASE:-https://findata.xhhan.com}"
[ "${MACRO_SKIP_API:-0}" = "1" ] && USE_API=false
case " $ARGUMENTS " in *" --no-api "*) USE_API=false ;; esac
for tok in $ARGUMENTS; do case "$tok" in --api-base=*) API_BASE="${tok#--api-base=}" ;; esac; done
echo "TODAY=$TODAY DATA=$DATA PREV=${PREV:-없음} P=$P use_api=$USE_API api_base=$API_BASE"
```

## Step 1: 뉴스 헤드라인 (Bash)

데이터 플랫폼이 3시간마다 누적한 RSS 헤드라인에서 한 주치를 거시 관련만 걸러 파일로 만든다. 헤드라인 API 는 **내부망 전용**이라 scanner(WebFetch) 가 직접 부를 수 없다.

```bash
SINCE="${PREV:-$(date -d "$TODAY -7 day" '+%Y-%m-%d')}"
python3 "$P/scripts/fetch_headlines.py" --since "$SINCE" --out "$DATA/뉴스헤드라인.md" \
  || echo "헤드라인 실패 — outlook scanner 가 WebSearch 로 대신한다"
```

## Step 2: 데이터 수집 (macro-scanner × 5, 한 메시지에서 병렬)

| report_type | question_template_path | scan_data_path |
|---|---|---|
| liquidity | `$REF/question-liquidity.md` | `$DATA/liquidity.md` |
| regime | `$REF/question-regime.md` | `$DATA/regime.md` |
| sector | `$REF/question-sector.md` | `$DATA/sector.md` |
| insider | `$REF/question-insider.md` | `$DATA/insider.md` |
| outlook | `$REF/question-outlook.md` | `$DATA/outlook.md` |

각 scanner 에 함께 전달:
- `previous_data_path`: `$OUT/데이터/$PREV/<type>.md` (PREV 가 있을 때). `outlook` 은 `$OUT/데이터/$PREV/판단.md` 도
- `headlines_path` (`outlook` 만): `$DATA/뉴스헤드라인.md`
- `use_api`, `api_base_url`: Step 0 값

각 scanner 는 파일을 Write 하고 **"저장 완료: 경로"** 한 줄만 보고한다. 오케스트레이터는 내용을 읽지 않는다.

Agent 타입 `macro-report:macro-scanner` 가 없으면 `$P/agents/macro-scanner.md` 본문을 `general-purpose` 에이전트 프롬프트에 넣어 같은 입력으로 호출한다.

## Step 3: 데이터 갭 전송 (선택, 실패 무시)

```bash
# NAS 환경은 FDP_REPORTER_API_KEY 로 주입된다 (1.x 는 FDP_API_KEY 만 찾았다)
KEY="${FDP_API_KEY:-${FDP_REPORTER_API_KEY:-}}"
if [ -n "$KEY" ] && [ "$USE_API" = "true" ]; then
  TMP_GAP="${TMPDIR:-/tmp}/_macro_gap_$$.json"; posted=0; failed=0
  for f in "$DATA"/*_data_gaps.jsonl; do
    [ -f "$f" ] || continue
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      printf '%s' "$line" > "$TMP_GAP"   # 한글 UTF-8 보존 (#5)
      if curl -fsS -m 5 -X POST "$API_BASE/api/meta/data-gaps" -H "Content-Type: application/json" \
           -H "X-API-Key: $KEY" --data-binary @"$TMP_GAP" >/dev/null 2>&1
      then posted=$((posted+1)); else failed=$((failed+1)); fi
    done < "$f"
  done
  rm -f "$TMP_GAP"; echo "data_gaps: posted=$posted failed=$failed"
fi
```

명명 규약은 `references/data-gaps-conventions.md`.

## Step 4: 확인·보고

```bash
for t in liquidity regime sector insider outlook; do
  [ -s "$DATA/$t.md" ] && echo "OK $t" || echo "누락 $t"
done
```

빠진 유형은 scanner 를 **한 번만** 다시 호출한다. 그래도 빠지면 그대로 두고 보고에 적는다 (2부는 3개 이상이면 진행).

보고: 생성 파일 수(n/5)·누락 목록·헤드라인 건수 — 세 줄.
