---
name: classify
description: 보유 종목을 투자원칙 v2 보유 유형으로 분류하고 투자 사유·훼손 조건 초안 노트를 만든다 (가벼운 분류 모드)
argument-hint: "[TICKER ...] | --holdings [--only-missing]"
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - Agent
---

# Classify Command — 보유 분류 모드

전체 종목분석(`analyze`) 대신 **유형 판정 + 투자 사유 초안**만 빠르게 만든다. 결과는 종목마다 보유분류 노트 하나.

## 인자

- `TICKER ...`: 분류할 티커들
- `--holdings`: 토스 보유 전체 (toss-holdings DB 의 최신 스냅샷). `--only-missing` 이면 노트가 없는 종목만

## Step 0: 준비

```bash
V="${OBSIDIAN_VAULT:-$PWD}"
P="${CLAUDE_PLUGIN_ROOT:-$(ls -d ~/.claude/plugins/cache/elhaz-plugins/stock-analysis/*/ | sort -V | tail -1)}"; P="${P%/}"
PRINCIPLES="$V/02_Areas/생활/재정관리/투자원칙 v2.md"
FORMAT="$P/skills/stock-analysis-workflow/references/holding-classification.md"
DCF="$P/scripts/reverse_dcf.py"
OUT="$V/03_Resources/주식분석/보유분류"; mkdir -p "$OUT"
ls "$PRINCIPLES" "$FORMAT" "$DCF"
```

원칙 문서가 없으면 멈추고 알린다 (판정 기준 없이 분류하지 않는다).

## Step 1: 종목 목록

- 티커 인자면 그대로
- `--holdings` 면 NAS 의 toss-holdings DB 에서 최신 스냅샷 종목을 읽는다. 시가총액은 토스 `/api/v1/stocks` 의 `sharesOutstanding × last_price` 로 구해 넘긴다 (ETF·ADR 은 비움). 자동매수 가능 여부는 최근 30일 자동매수 주문 유무로 추정하되, 없다고 곧 `불가` 로 보지 않는다 — 기존 노트 값을 우선한다
- `--holdings` 목록은 아래로 뽑는다 (NAS 전용 — 토스 API 는 허용 IP 에서만 됨):

```bash
cd /home/xhh/toss-holdings && set -a && . /home/xhh/docker/toss-holdings/.env && set +a && python3 - <<'PY'
import sqlite3, json, toss_holdings as th
c = sqlite3.connect("data/holdings.db")
d = c.execute("select max(snap_date) from snapshots").fetchone()[0]
pos = c.execute("select symbol, name, last_price from positions where snap_date=?", (d,)).fetchall()
auto = {r[0] for r in c.execute("select distinct symbol from orders where side='BUY' and status='FILLED' and ordered_at >= date(?, '-30 day')", (d,))}
info = {i["symbol"]: i for i in th.Client().get("/api/v1/stocks", query={"symbols": ",".join(p[0] for p in pos)})}
for sym, name, px in pos:
    i = info.get(sym, {}); so = i.get("sharesOutstanding")
    cap = round(float(so) * px / 1e9, 2) if so and i.get("securityType") == "STOCK" else None
    print(json.dumps({"ticker": sym, "종목명": name, "시총B": cap, "현재가": px,
                      "종류": i.get("securityType"), "최근자동매수": sym in auto}, ensure_ascii=False))
PY
```

- `--only-missing` 이면 `$OUT/*.md` 의 frontmatter `ticker` 와 비교해 없는 것만
- **금액·수량·비중은 에이전트에 넘기지 않는다**

## Step 2: 에이전트 배분

`stock-classifier` 에이전트를 **종목 5~6개씩 묶어 병렬로** 호출한다 (한 번에 최대 4개 에이전트). 각 호출에 넘길 것:

- 종목 목록 (티커, 한글 종목명, 시가총액 $B, 현재가, 자동매수 여부 — 아는 것만)
- `$PRINCIPLES`, `$FORMAT`, `$DCF`, `$OUT` 절대경로
- 오늘 날짜와 다음 재분류일 (다음 1·4·7·10월 첫 월요일)

## Step 3: 확인과 보고

```bash
python3 - "$OUT" <<'PY'
import sys, re, pathlib, collections
c = collections.Counter(); missing = []
for f in pathlib.Path(sys.argv[1]).glob("*.md"):
    m = re.search(r"^보유유형:\s*(\S+)", f.read_text(), re.M)
    (c.update([m.group(1)]) if m else missing.append(f.name))
print(dict(c), "frontmatter 누락:", missing)
PY
```

사용자에게 유형별 개수와 **경계선 종목**, 초안이라 사유를 고쳐야 한다는 안내만 짧게 보고한다. 노트 전문은 붙이지 않는다.

## 예

```
/stock-analysis:classify PLTR KO
/stock-analysis:classify --holdings --only-missing
```
