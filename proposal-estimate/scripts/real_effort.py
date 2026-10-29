"""실작업 계산 — PM 페르소나 견적(JSON)에 일 종류별 배율을 곱한다.

견적 = AI 없이 사람이 하는 시간(PM 페르소나 값, 금액 근거)
실작업 = 견적 × 배율, 0.5 MD 단위 반올림 (일정 · 원가 근거, 배율은 가정)

행마다 `kind` (dev / logic / analysis / meeting) 가 있어야 한다.
행에 없으면 그 행이 속한 `sections[].kind` 를 쓴다. 둘 다 없으면 멈추고 목록을 보여 준다.
kind 는 PM 페르소나가 아니라 세션이 붙인다(배율은 세션 몫).

사용:
    python real_effort.py pm_estimate.json -o result.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimate_config  # noqa: E402


T = estimate_config.tilde


def f1(x):
    return f"{x:.1f}"


def sections_of(d):
    # sections 가 없으면 rows 에 나온 순서대로 만든다
    if d.get("sections"):
        return d["sections"]
    seen, out = set(), []
    for r in d["rows"]:
        if r["section"] not in seen:
            seen.add(r["section"])
            out.append({"key": r["section"], "name": r["section"]})
    return out


def compute(d, cfg):
    factors = {k: v["factor"] for k, v in cfg["factors"].items()}
    unit = cfg.get("rounding_md", 0.5)
    secs = sections_of(d)
    sec_kind = {s["key"]: s.get("kind") for s in secs}

    missing = [r["id"] for r in d["rows"] if not (r.get("kind") or sec_kind.get(r["section"]))]
    if missing:
        raise ValueError("kind 가 없는 행: " + ", ".join(missing))
    unknown = sorted({r.get("kind") or sec_kind[r["section"]] for r in d["rows"]} - set(factors))
    if unknown:
        raise ValueError("설정에 없는 kind: " + ", ".join(unknown))
    keys = {s["key"] for s in secs}
    stray = [r["id"] for r in d["rows"] if r["section"] not in keys]
    if stray:
        raise ValueError("sections 에 없는 section 을 쓴 행: " + ", ".join(stray))

    res = {"sections": [], "by_kind": {k: [] for k in factors}, "rows": []}
    tot_e = tot_r = 0.0
    for s in secs:
        rows = [r for r in d["rows"] if r["section"] == s["key"]]
        lines = ["| # | 항목 | **견적** | 실작업 | 근거 |", "|---|---|---:|---:|---|"]
        se = sr = 0.0
        for r in rows:
            kind = r.get("kind") or sec_kind[s["key"]]
            real = estimate_config.round_md(r["md"] * factors[kind], unit)
            res["by_kind"][kind].append(r["id"])
            res["rows"].append({"id": r["id"], "md": r["md"], "real": real, "kind": kind})
            se += r["md"]
            sr += real
            lines.append(f"| {r['id']} | {T(r['item'])} | **{f1(r['md'])}** | {f1(real)} | {T(r.get('basis', ''))} |")
        lines.append(f"| | **소계** | **{f1(se)}** | {f1(sr)} | |")
        res["sections"].append({"key": s["key"], "name": s["name"], "est": se, "real": sr, "table": "\n".join(lines)})
        tot_e += se
        tot_r += sr

    # 회의는 AI 로 줄지 않는다: 견적과 실작업이 같다
    ml = ["| # | 회의 | **견적 · 실작업** | 비고 |", "|---|---|---:|---|"]
    ms = 0.0
    meet_factor = factors.get("meeting", 1.0)
    for m in d.get("meetings", []):
        ms += m["md"]
        ml.append(f"| {m['id']} | {T(m['item'])} | **{f1(m['md'])}** | {T(m.get('note', ''))} |")
    ml.append(f"| | **합계** | **{f1(ms)}** | |")
    meet_real = estimate_config.round_md(ms * meet_factor, unit)

    tot_e += ms
    tot_r += meet_real
    rate = cfg["rate"]
    days = rate["workdays_per_month"]
    res.update(
        meet=("\n".join(ml)),
        meet_md=ms,
        meet_real=meet_real,
        total_est=tot_e,
        total_real=tot_r,
        mm_est=round(tot_e / days, 2),
        mm_real=round(tot_r / days, 2),
        amount_est=round(tot_e * rate["daily_won"]),
        amount_real=round(tot_r * rate["daily_won"]),
    )
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="견적 JSON 에 배율을 곱해 실작업을 계산한다")
    ap.add_argument("pm_json")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--config", help="설정 덮어쓰기 파일")
    a = ap.parse_args(argv)

    cfg = estimate_config.load(a.config)
    d = json.loads(Path(a.pm_json).read_text(encoding="utf-8"))
    try:
        res = compute(d, cfg)
    except ValueError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 3
    Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(
        f"견적 {f1(res['total_est'])} MD ({res['mm_est']:.2f} M/M) {res['amount_est']:,}원 / "
        f"실작업 {f1(res['total_real'])} MD ({res['mm_real']:.2f} M/M) {res['amount_real']:,}원"
    )
    for k, ids in res["by_kind"].items():
        if ids:
            print(f"  {k} x{cfg['factors'][k]['factor']}: {' '.join(ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
