#!/usr/bin/env python3
"""거시경제 주간 보고 v2 — 판단 파일 검증 · 예측 채점 · 차트 생성.

표준 라이브러리만 쓴다 (루틴 환경에 pandas 가 없다).

사용:
    weekly_score.py validate <판단.md>
    weekly_score.py score --data-root <분석/데이터> --date YYYY-MM-DD [--out <채점.md>]

판단 파일(`데이터/{날짜}/판단.md`)의 ```json 블록이 예측 원장이다. 별도 원장
파일은 두지 않고, 매주 score 가 모든 판단 파일을 훑어 만기가 된 예측을 채점한다.
실제값은 financial-data-platform API 에서 받는다 (FDP_API_BASE, 기본은 NAS
로컬 → 공개 주소 순).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

# -------------------- 예측 대상 (단일 출처: references/judgment-schema.md) --------------------

# 비중안에 쓸 수 있는 티커 = 자산군 4 + 상대 성과 예측 20
ASSET_CLASS = ["SPY", "TLT", "SHY", "GLD"]
RELATIVE = [
    "XLK", "XLF", "XLV", "XLE", "XLY", "XLP", "XLI", "XLB", "XLU", "XLRE", "XLC",
    "SMH", "IWM", "EWY", "EFA", "EEM", "XBI", "KRE", "ITB", "ITA",
]
SECTORS = RELATIVE[:11]
ALLOCATABLE = ASSET_CLASS + RELATIVE
BENCHMARK_6040 = {"SPY": 60, "IEF": 40}

# 거시 변수: (데이터 종류, 심볼, 변환, '유지' 폭). 폭 안의 변화는 flat.
#   변환 level = 수준 차이, pct = 변화율(%), yoy = 전년비(%)의 차이
MACRO = {
    "FEDFUNDS": ("indicator", "FEDFUNDS", "level", 0.125),
    "DGS10": ("indicator", "DGS10", "level", 0.10),
    "CPI": ("indicator", "CPIAUCSL", "yoy", 0.2),
    "SPY": ("price", "SPY", "pct", 2.0),
    "WTI": ("price", "CL=F", "pct", 5.0),
    "VIX": ("price", "^VIX", "level", 2.0),
    "USDKRW": ("price", "KRW=X", "pct", 1.0),
    "KOSPI": ("price", "^KS11", "pct", 2.0),
    "GOLD": ("price", "GC=F", "pct", 3.0),
    "HY_SPREAD": ("indicator", "BAMLH0A0HYM2", "level", 0.25),
    "UNRATE": ("indicator", "UNRATE", "level", 0.1),
}
DIRECTIONS = {"up", "down", "flat"}

HORIZONS = {"h1m": 30, "h3m": 91, "h6m": 182}
HORIZON_LABEL = {"h1m": "1개월", "h3m": "3개월", "h6m": "6개월"}

# 만기일 기준 이 일수 안의 관측값이 있어야 채점한다 (휴장·발표 지연 허용)
PRICE_TOLERANCE_DAYS = 5
# 월간 지표와 발표 지연 (관측월 1일 → 다음 달 중순 발표)
MONTHLY = {"FEDFUNDS", "CPI", "UNRATE"}
MONTHLY_RELEASE_LAG = 45

JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.S)


# -------------------- 판단 파일 --------------------

def load_judgment(path: Path) -> dict:
    """판단.md 의 첫 ```json 블록을 읽는다."""
    m = JSON_BLOCK.search(path.read_text(encoding="utf-8"))
    if not m:
        raise ValueError(f"{path}: ```json 블록이 없다")
    return json.loads(m.group(1))


def validate(j: dict) -> list[str]:
    """스키마 위반 목록. 비어 있으면 통과."""
    errs: list[str] = []

    def need(key, typ):
        if not isinstance(j.get(key), typ):
            errs.append(f"'{key}' 가 없거나 {typ.__name__} 가 아니다")
            return False
        return True

    if j.get("version") != 2:
        errs.append("version 은 2")
    if need("report_date", str):
        try:
            date.fromisoformat(j["report_date"])
        except ValueError:
            errs.append("report_date 형식은 YYYY-MM-DD")

    source_ids: set = set()
    if need("sources", list):
        for s in j["sources"]:
            if not isinstance(s, dict) or not {"id", "publisher", "date", "url"} <= s.keys():
                errs.append(f"sources 항목에 id/publisher/date/url 필요: {s}")
            else:
                source_ids.add(s["id"])

    def check_basis(item, where):
        basis = item.get("basis", [])
        if not isinstance(basis, list) or not basis:
            errs.append(f"{where}: basis(근거 출처 id 목록)가 비었다")
        for b in basis if isinstance(basis, list) else []:
            if b not in source_ids:
                errs.append(f"{where}: basis {b} 가 sources 에 없다")

    if need("allocation", dict):
        alloc = j["allocation"]
        bad = [t for t in alloc if t not in ALLOCATABLE]
        if bad:
            errs.append(f"allocation 에 허용되지 않은 티커: {bad}")
        if any(not isinstance(w, (int, float)) or w < 0 for w in alloc.values()):
            errs.append("allocation 비중은 0 이상의 숫자")
        elif abs(sum(alloc.values()) - 100) > 0.01:
            errs.append(f"allocation 합계가 100 이 아니다: {sum(alloc.values())}")

    if need("relative", list):
        seen = [r.get("ticker") for r in j["relative"]]
        missing = sorted(set(RELATIVE) - set(seen))
        extra = sorted(set(seen) - set(RELATIVE))
        if missing:
            errs.append(f"relative 누락: {missing}")
        if extra:
            errs.append(f"relative 에 대상 밖 티커: {extra}")
        if len(seen) != len(set(seen)):
            errs.append("relative 에 중복 티커")
        for r in j["relative"]:
            for h in HORIZONS:
                p = r.get(h)
                if not isinstance(p, (int, float)) or not 0 <= p <= 1:
                    errs.append(f"relative {r.get('ticker')} {h}: 0~1 확률이어야 한다 ({p})")
            check_basis(r, f"relative {r.get('ticker')}")

    if need("macro", list):
        seen = [m.get("var") for m in j["macro"]]
        missing = sorted(set(MACRO) - set(seen))
        if missing:
            errs.append(f"macro 누락: {missing}")
        extra = sorted(set(seen) - set(MACRO))
        if extra:
            errs.append(f"macro 에 대상 밖 변수: {extra}")
        for m in j["macro"]:
            for h in HORIZONS:
                if m.get(h) not in DIRECTIONS:
                    errs.append(f"macro {m.get('var')} {h}: up/down/flat 중 하나 ({m.get(h)})")
            check_basis(m, f"macro {m.get('var')}")

    # 섹터 11개는 S&P 500 을 나눠 가지므로 전부 한쪽일 수 없다
    if isinstance(j.get("relative"), list):
        sectors = [r for r in j["relative"] if isinstance(r, dict) and r.get("ticker") in SECTORS]
        for h in HORIZONS:
            ps = [r.get(h) for r in sectors if isinstance(r.get(h), (int, float))]
            if len(ps) == len(SECTORS) and (all(p > 0.5 for p in ps) or all(p < 0.5 for p in ps)):
                errs.append(f"섹터 11개 {h} 확률이 전부 0.5 한쪽이다 — 섹터 합이 곧 S&P 500")

    if need("scenarios", list):
        if len(j["scenarios"]) != 3:
            errs.append(f"scenarios 는 기본·상방·하방 3개 ({len(j['scenarios'])}개)")
        total = sum(s.get("prob", 0) for s in j["scenarios"] if isinstance(s, dict))
        if abs(total - 1) > 0.01:
            errs.append(f"scenarios 확률 합이 1 이 아니다: {total}")
    return errs


def iter_judgments(data_root: Path):
    """(날짜, 판단 dict) 를 날짜 오름차순으로. 읽기 실패는 경고만."""
    for p in sorted(data_root.glob("*/판단.md")):
        try:
            j = load_judgment(p)
            date.fromisoformat(j["report_date"])
            yield j["report_date"], j
        except Exception as e:  # noqa: BLE001 — 한 주 파손으로 전체 채점을 멈추지 않는다
            print(f"경고: {p} 건너뜀 — {e}", file=sys.stderr)


# -------------------- 데이터 플랫폼 --------------------

class FDP:
    def __init__(self, base: str | None = None):
        candidates = [base] if base else [
            os.getenv("FDP_API_BASE"), "http://localhost:8000", "https://stock.xhhan.com",
        ]
        self.base = None
        for c in filter(None, candidates):
            try:
                self._get(c, "/api/health")
                self.base = c
                break
            except Exception:  # noqa: BLE001
                continue
        if self.base is None:
            raise RuntimeError(f"데이터 플랫폼에 연결할 수 없다: {candidates}")
        self._cache: dict = {}

    @staticmethod
    def _get(base: str, path: str) -> dict:
        req = urllib.request.Request(
            base + path, headers={"User-Agent": "macro-report-score/2.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    def series(self, kind: str, symbol: str) -> list[tuple[date, float]]:
        """심볼 전체 시계열 (최근 약 3년). 심볼당 한 번만 호출하고 캐시한다."""
        key = (kind, symbol)
        if key not in self._cache:
            path = "prices" if kind == "price" else "indicators"
            qs = urllib.parse.urlencode({
                "start_date": (date.today() - timedelta(days=1100)).isoformat(),
                "end_date": (date.today() + timedelta(days=1)).isoformat(),
                "limit": 5000,
            })
            try:
                body = self._get(self.base, f"/api/{path}/{urllib.parse.quote(symbol, safe='')}?{qs}")
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    raise
                body = {"columns": [], "data": []}
            cols = body.get("columns", [])
            col = next((cols.index(c) for c in ("close", "value") if c in cols), None)
            rows = [] if col is None else [
                (date.fromisoformat(r[0]), float(r[col])) for r in body["data"] if r[col] is not None
            ]
            self._cache[key] = sorted(rows)
        return self._cache[key]

    def value_at(self, kind: str, symbol: str, day: date, tolerance: int) -> float | None:
        """day 이하의 가장 최근 관측값. tolerance 일보다 오래됐으면 None."""
        rows = [r for r in self.series(kind, symbol) if r[0] <= day]
        if not rows or (day - rows[-1][0]).days > tolerance:
            return None
        return rows[-1][1]

    def macro_value(self, var: str, day: date) -> float | None:
        """day 시점에 알 수 있던 거시 변수 값.

        월간 지표는 관측월(1일자) 다음 달 중순에 발표되므로, 관측일 +45일 이전에는
        모르는 값으로 본다. 그렇지 않으면 판단일 기준값에 그 뒤 발표된 값이 섞인다.
        """
        kind, symbol, transform, _ = MACRO[var]
        if var not in MONTHLY:
            return self.value_at(kind, symbol, day, PRICE_TOLERANCE_DAYS)
        rows = [r for r in self.series(kind, symbol)
                if r[0] + timedelta(days=MONTHLY_RELEASE_LAG) <= day]
        if not rows:
            return None
        latest_day, latest = rows[-1]
        if transform != "yoy":
            return latest
        year_ago = [v for d, v in rows if d <= date(latest_day.year - 1, latest_day.month, 1)]
        return None if not year_ago else (latest / year_ago[-1] - 1) * 100


# -------------------- 채점 --------------------

def _ret(fdp: FDP, ticker: str, start: date, end: date) -> float | None:
    a = fdp.value_at("price", ticker, start, PRICE_TOLERANCE_DAYS)
    b = fdp.value_at("price", ticker, end, PRICE_TOLERANCE_DAYS)
    if a is None or b is None:
        return None
    return (b / a - 1) * 100


def _direction(var: str, before: float, after: float) -> str:
    _, _, transform, band = MACRO[var]
    change = (after / before - 1) * 100 if transform == "pct" else after - before
    if change > band:
        return "up"
    if change < -band:
        return "down"
    return "flat"


def score_all(fdp: FDP, judgments: list[tuple[str, dict]], today: date) -> dict:
    """만기가 지난 모든 예측을 채점."""
    rel_rows, alloc_rows, macro_rows = [], [], []
    for rd, j in judgments:
        base = date.fromisoformat(rd)
        for h, days in HORIZONS.items():
            due = base + timedelta(days=days)
            if due >= today:
                continue
            spy = _ret(fdp, "SPY", base, due)
            for r in j["relative"]:
                ret = _ret(fdp, r["ticker"], base, due)
                if ret is None or spy is None:
                    continue
                outcome = 1 if ret > spy else 0
                rel_rows.append({
                    "report_date": rd, "h": h, "ticker": r["ticker"], "p": r[h],
                    "excess": ret - spy, "outcome": outcome, "brier": (r[h] - outcome) ** 2,
                })
            port = [(_ret(fdp, t, base, due), w) for t, w in j["allocation"].items() if w]
            bench = [(_ret(fdp, t, base, due), w) for t, w in BENCHMARK_6040.items()]
            if all(r is not None for r, _ in port + bench):
                p_ret = sum(r * w for r, w in port) / 100
                b_ret = sum(r * w for r, w in bench) / 100
                alloc_rows.append({"report_date": rd, "h": h, "ret": p_ret, "bench": b_ret})
            for m in j["macro"]:
                before, after = fdp.macro_value(m["var"], base), fdp.macro_value(m["var"], due)
                if before is None or after is None:
                    continue
                actual = _direction(m["var"], before, after)
                macro_rows.append({
                    "report_date": rd, "h": h, "var": m["var"], "pred": m[h],
                    "actual": actual, "hit": m[h] == actual,
                })
    return {"relative": rel_rows, "allocation": alloc_rows, "macro": macro_rows}


# -------------------- 출력 --------------------

def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _pct(flags):
    """참 비율(%). 비어 있으면 None."""
    return None if not flags else sum(1 for f in flags if f) / len(flags) * 100


def _fmt(x, digits=1, suffix=""):
    return "—" if x is None else f"{x:+.{digits}f}{suffix}" if suffix == "%p" else f"{x:.{digits}f}{suffix}"


def chart_relative(j: dict) -> dict:
    """차트 ①: 이번 주 ETF 3개월 전망 — S&P 500 보다 잘할 확률."""
    rows = sorted(j["relative"], key=lambda r: r["h3m"])
    xs = [round((r["h3m"] - 0.5) * 100, 1) for r in rows]
    return {
        "data": [{
            "type": "bar", "orientation": "h",
            "y": [r["ticker"] for r in rows], "x": xs,
            "text": [f"{round(r['h3m'] * 100)}%" for r in rows], "textposition": "outside",
            "marker": {"color": ["#43A047" if x > 0 else "#E53935" if x < 0 else "#9E9E9E" for x in xs]},
        }],
        "layout": {
            "title": {"text": "3개월 뒤 S&P 500 보다 잘할 확률 (50% 기준)", "font": {"size": 14}},
            "xaxis": {"title": "50% 대비 (%p)", "zeroline": True, "range": [-50, 50]},
            "height": 520, "margin": {"l": 60, "r": 30, "t": 50, "b": 40},
        },
    }


def chart_allocation(judgments: list[tuple[str, dict]]) -> dict:
    """차트 ②: 주별 비중 변화 (자산군 묶음 누적)."""
    groups = {"미국 주식(SPY)": ["SPY"], "업종·지역 ETF": RELATIVE, "장기채(TLT)": ["TLT"],
              "단기채(SHY)": ["SHY"], "금(GLD)": ["GLD"]}
    colors = {"미국 주식(SPY)": "#1E88E5", "업종·지역 ETF": "#8E24AA", "장기채(TLT)": "#FB8C00",
              "단기채(SHY)": "#90A4AE", "금(GLD)": "#FDD835"}
    recent = judgments[-12:]
    dates = [rd for rd, _ in recent]
    data = []
    for name, tickers in groups.items():
        data.append({
            "type": "scatter", "mode": "lines", "stackgroup": "one", "name": name,
            "x": dates, "y": [sum(j["allocation"].get(t, 0) for t in tickers) for _, j in recent],
            "line": {"color": colors[name]},
        })
    return {
        "data": data,
        "layout": {
            "title": {"text": "주별 비중 변화 (최근 12주, %)", "font": {"size": 14}},
            "yaxis": {"range": [0, 100], "ticksuffix": "%"}, "height": 380,
            "margin": {"l": 50, "r": 20, "t": 50, "b": 40},
        },
    }


def render(score: dict, judgments: list[tuple[str, dict]], target: dict, today: date) -> str:
    rel, alloc, mac = score["relative"], score["allocation"], score["macro"]
    lines = [f"# 채점 결과 ({today.isoformat()})", "",
             "> weekly_score.py 가 생성. 보고서에는 표·차트를 그대로 옮긴다.", ""]

    lines += ["## 지난 예측 성적", ""]
    if not (rel or alloc or mac):
        lines += ["아직 만기가 된 예측이 없다 (첫 1개월 채점은 첫 보고서 30일 뒤).", ""]
    else:
        lines += ["| 기간 | ETF 확률 예측 (Brier, 낮을수록 좋음 · 기준 0.25) | 방향 적중률 | 비중안 vs 60/40 (평균 초과수익) | 비중안 승률 | 거시 방향 적중률 |",
                  "|---|---|---|---|---|---|"]
        for h in HORIZONS:
            r = [x for x in rel if x["h"] == h]
            a = [x for x in alloc if x["h"] == h]
            m = [x for x in mac if x["h"] == h]
            if not (r or a or m):
                continue
            decided = [x for x in r if x["p"] != 0.5]
            hit = _pct([(x["p"] > 0.5) == (x["outcome"] == 1) for x in decided])
            excess = _mean([x["ret"] - x["bench"] for x in a])
            lines.append(
                f"| {HORIZON_LABEL[h]} | {_fmt(_mean([x['brier'] for x in r]), 3)} ({len(r)}건) "
                f"| {_fmt(hit, 0, '%')} | {_fmt(excess, 2, '%p')} ({len(a)}주) "
                f"| {_fmt(_pct([x['ret'] > x['bench'] for x in a]), 0, '%')} "
                f"| {_fmt(_pct([x['hit'] for x in m]), 0, '%')} ({len(m)}건) |"
            )
        lines += ["", "- Brier 0.25 = 항상 50% 라고 찍은 수준. 이보다 낮아야 예측에 의미가 있다.",
                  "- 비중안은 판단일 종가에 사서 만기일 종가까지 들고 있었다고 가정. 60/40 = SPY 60 · IEF 40.", ""]

        newest = max((x["report_date"] for x in rel + alloc), default=None)
        if newest:
            lines += [f"### 이번에 새로 만기 된 비중안 ({newest} 판단 이전 포함, 최근 5건)", "",
                      "| 판단일 | 기간 | 비중안 | 60/40 | 차이 |", "|---|---|---|---|---|"]
            for x in sorted(alloc, key=lambda x: (x["report_date"], x["h"]))[-5:]:
                lines.append(f"| {x['report_date']} | {HORIZON_LABEL[x['h']]} | {x['ret']:+.2f}% "
                             f"| {x['bench']:+.2f}% | {x['ret'] - x['bench']:+.2f}%p |")
            lines.append("")

    lines += ["## 차트 ① 이번 주 ETF 전망", "", "```plotly",
              json.dumps(chart_relative(target), ensure_ascii=False, indent=1), "```", "",
              "## 차트 ② 주별 비중 변화", "", "```plotly",
              json.dumps(chart_allocation(judgments), ensure_ascii=False, indent=1), "```", ""]
    return "\n".join(lines)


# -------------------- CLI --------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="판단.md 스키마 검증")
    v.add_argument("path", type=Path)
    s = sub.add_parser("score", help="만기 예측 채점 + 차트 → 채점.md")
    s.add_argument("--data-root", type=Path, required=True, help="분석/데이터 디렉토리")
    s.add_argument("--date", required=True, help="이번 판단일 (YYYY-MM-DD)")
    s.add_argument("--out", type=Path, help="기본: <data-root>/<date>/채점.md")
    s.add_argument("--api-base", help="데이터 플랫폼 주소 (기본 FDP_API_BASE → localhost → 공개 주소)")
    s.add_argument("--today", help="채점 기준일 (기본 오늘, 테스트용)")
    args = ap.parse_args()

    if args.cmd == "validate":
        errs = validate(load_judgment(args.path))
        for e in errs:
            print(f"- {e}")
        print("통과" if not errs else f"실패 {len(errs)}건")
        return 0 if not errs else 1

    judgments = list(iter_judgments(args.data_root))
    target = next((j for rd, j in judgments if rd == args.date), None)
    if target is None:
        print(f"{args.date} 판단 파일이 없다 — 판단.md 를 먼저 쓴다", file=sys.stderr)
        return 1
    errs = validate(target)
    if errs:
        print("판단 파일 검증 실패:\n" + "\n".join(f"- {e}" for e in errs), file=sys.stderr)
        return 1
    today = date.fromisoformat(args.today) if args.today else date.today()
    fdp = FDP(args.api_base)
    result = score_all(fdp, judgments, today)
    out = args.out or args.data_root / args.date / "채점.md"
    out.write_text(render(result, judgments, target, today), encoding="utf-8")
    print(f"저장 완료: {out} (데이터 플랫폼 {fdp.base}, 채점 ETF {len(result['relative'])}건 · "
          f"비중안 {len(result['allocation'])}건 · 거시 {len(result['macro'])}건)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
