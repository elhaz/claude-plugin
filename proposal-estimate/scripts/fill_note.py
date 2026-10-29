"""공수 산정 노트 채우기 — 템플릿의 {{자리}} 를 PM 견적 JSON 과 실작업 계산 결과로 채운다.

옵션 · 축소안 합계, 금액, 일정(주)을 여기서 계산한다. 손으로 더하지 않는다.
글로 쓰는 부분(가정, 입력 자료, 착수 전에 정할 것)은 세션이 템플릿 사본에 먼저 적어 둔다.

사용:
    python fill_note.py 템플릿사본.md pm_estimate.json result.json -o 노트.md

남은 {{자리}} 가 있으면 멈춘다. 쓸 수 있는 자리 이름은 --list 로 본다.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estimate_config  # noqa: E402

SLOT = re.compile(r"\{\{([a-z0-9_]+)\}\}")


def f1(x):
    return f"{x:.1f}"


def won(x):
    return f"{round(x):,}"


tilde = estimate_config.tilde



def signed(x):
    return f1(x).replace("-", "−")


def build(d, r, cfg):
    rate = cfg["rate"]
    day = rate["daily_won"]
    fac = cfg["factors"]
    v = {}

    # 요약 숫자
    v.update(
        total_est=f1(r["total_est"]), mm_est=f"{r['mm_est']:.2f}", meet_md=f1(r["meet_md"]),
        amount_est=won(r["amount_est"]), total_real=f1(r["total_real"]), mm_real=f"{r['mm_real']:.2f}",
        amount_real=won(r["amount_real"]), days_per_month=f"{rate['workdays_per_month']:g}",
        rate_grade=rate["grade"], rate_daily=won(rate["daily_won"]), rate_monthly=won(rate["monthly_won"]),
        rate_source_file=rate.get("source_file", ""),
    )

    # 배율 표
    ft = ["| 일의 종류 | 실작업 ÷ 견적 (가정) | 해당 항목 |", "|---|---:|---|"]
    for k, meta in fac.items():
        ids = list(r["by_kind"].get(k, []))
        if k == "meeting" and d.get("meetings"):
            ids = [m["id"] for m in d["meetings"]] + ids
        note = " (AI 로 줄지 않는다)" if meta["factor"] >= 1.0 else ""
        ft.append(f"| {meta['label']} | {float(meta['factor'])}{note} | {', '.join(ids) or '없음'} |")
    v["factor_table"] = "\n".join(ft)

    # 기능 분해 절
    secs = [f"### 1.{i} {s['name']}\n\n{s['table']}" for i, s in enumerate(r["sections"], 1)]
    v["sections"] = "\n\n".join(secs)
    v["uncertain_no"] = f"1.{len(r['sections']) + 1}"

    unc = ["| 항목 | 견적 범위 (MD) | 이유 |", "|---|---|---|"]
    for u in d.get("uncertain", []):
        unc.append(f"| {tilde(u['item'])} | {tilde(u['range'])} | {tilde(u['reason'])} |")
    v["uncertain"] = "\n".join(unc)

    v["meet"] = r["meet"]

    tot = ["| 구분 | **견적** | 실작업 |", "|---|---:|---:|"]
    for s in r["sections"]:
        tot.append(f"| {s['name']} | **{f1(s['est'])}** | {f1(s['real'])} |")
    if d.get("meetings"):
        tot.append(f"| 회의 | **{f1(r['meet_md'])}** | {f1(r['meet_real'])} |")
    tot.append(f"| **합계 MD** | **{f1(r['total_est'])}** | **{f1(r['total_real'])}** |")
    tot.append(f"| **M/M (÷{rate['workdays_per_month']:g})** | **{r['mm_est']:.2f}** | {r['mm_real']:.2f} |")
    v["total"] = "\n".join(tot)

    v["rate_table"] = "\n".join([
        "| 항목 | 값 |", "|---|---|",
        f"| 적용 단가 | {rate['grade']} **일 {won(rate['daily_won'])}원 / 월 {won(rate['monthly_won'])}원** |",
        f"| 근거 | {rate['source']} |",
        f"| 적용 기간 | {tilde(rate.get('applies', ''))} |",
        f"| M/M 환산 | 같은 자료의 월평균 근무일수 {rate['workdays_per_month']:g}일 |",
        f"| 원문 | `{rate.get('source_file', '')}` |",
    ])

    # 옵션
    opt = ["| 옵션 | 추가 견적 MD | 금액 (VAT 별도) | 근거 |", "|---|---:|---:|---|"]
    ot = 0.0
    for o in d.get("options", []):
        ot += o["md"]
        rng = f" ({tilde(o['range'])})" if o.get("range") else ""
        name = f"{o['id']} {o['item']}" if o.get("id") else o["item"]
        opt.append(f"| {tilde(name)} | +{f1(o['md'])}{rng} | {won(o['md'] * day)} | {tilde(o.get('basis', ''))} |")
    v["options"] = "\n".join(opt)
    v["opt_total"] = f1(ot)
    v["opt_amount"] = won(ot * day)

    inc = ["| 요인 | 추가 견적 MD | 근거 |", "|---|---|---|"]
    for x in d.get("increase", []):
        inc.append(f"| {tilde(x['factor'])} | {tilde(x['md'])} | {tilde(x.get('basis', ''))} |")
    v["increase"] = "\n".join(inc)

    # 1차 오픈 축소안: md 는 음수. rejected 는 취소선으로 남기고 합계에서 뺀다
    red = ["| 항목 | 견적 감소 | 조건 |", "|---|---:|---|"]
    rs = 0.0
    rejected = []
    for x in d.get("reduce", []):
        if x.get("skip"):
            continue
        md = -abs(x["md"])
        if x.get("rejected"):
            rejected.append(f"| ~~{tilde(x['item'])}~~ | ~~{signed(md)}~~ | 쓰지 않는다. {tilde(x.get('reason', ''))} |")
            continue
        rs += md
        red.append(f"| {tilde(x['item'])} | {signed(md)} | {tilde(x.get('condition', ''))} |")
    red.append(f"| **소계** | **{signed(rs)}** | |")
    red.extend(rejected)
    v["reduce"] = "\n".join(red)
    after = r["total_est"] + rs
    v["reduce_total"] = signed(rs)
    v["reduce_after"] = f1(after)
    v["reduce_amount"] = won(after * day)

    w = d.get("warranty") or {"md": 0, "basis": ""}
    v["warranty_md"] = f1(w["md"])
    v["warranty_amount"] = won(w["md"] * day)
    v["warranty_basis"] = w.get("basis", "")

    v["opinion"] = "\n".join(f"- {s}" for s in d.get("module_opinion", [])) or "- 없음"

    v["amount_table"] = "\n".join([
        "| 경우 | MD | 금액 (VAT 별도) |", "|---|---:|---:|",
        f"| 견적 전체 | {f1(r['total_est'])} | **{won(r['amount_est'])}** |",
        f"| 1차 오픈 축소안 모두 적용 | {f1(after)} | {won(after * day)} |",
        f"| 하자보수 · 안정화 (별도) | +{f1(w['md'])} | +{won(w['md'] * day)} |",
        f"| 원가 (실작업 {f1(r['total_real'])} MD × 단가) | {f1(r['total_real'])} | {won(r['amount_real'])} |",
    ])

    # 일정: 실작업 MD ÷ 주당 MD. 고객 회신 · 검수 기간은 따로 얹는다
    per_week = cfg.get("schedule", {}).get("md_per_week", 5)
    wk = r["total_real"] / per_week
    v["wk1"] = str(math.ceil(wk))
    v["wk2"] = str(math.ceil(wk / 2))
    return v


PROSE = "<<적을 것"


def fill(text, values):
    missing = sorted(set(SLOT.findall(text)) - set(values))
    if missing:
        raise KeyError("값이 없는 자리: " + ", ".join(missing))
    # 세션이 글로 채워야 할 자리가 남아 있으면 멈춘다
    left = [ln.strip() for ln in text.splitlines() if PROSE in ln]
    if left:
        raise KeyError("세션이 아직 적지 않은 자리: " + " / ".join(left[:3]))
    return SLOT.sub(lambda m: values[m.group(1)], text)


def main(argv=None):
    ap = argparse.ArgumentParser(description="공수 산정 노트 템플릿을 채운다")
    ap.add_argument("template", nargs="?")
    ap.add_argument("pm_json", nargs="?")
    ap.add_argument("result_json", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--config")
    ap.add_argument("--list", action="store_true", help="쓸 수 있는 자리 이름을 보여 준다")
    a = ap.parse_args(argv)

    cfg = estimate_config.load(a.config)
    if a.list:
        demo = {"rows": [], "sections": []}
        res = {"sections": [], "by_kind": {}, "meet": "", "meet_md": 0, "meet_real": 0, "total_est": 0,
               "total_real": 0, "mm_est": 0, "mm_real": 0, "amount_est": 0, "amount_real": 0}
        print("\n".join(sorted(build(demo, res, cfg))))
        return 0
    if not (a.template and a.pm_json and a.result_json and a.out):
        ap.error("template, pm_json, result_json, -o 가 필요하다")

    d = json.loads(Path(a.pm_json).read_text(encoding="utf-8"))
    r = json.loads(Path(a.result_json).read_text(encoding="utf-8"))
    text = Path(a.template).read_text(encoding="utf-8")
    try:
        out = fill(text, build(d, r, cfg))
    except KeyError as e:
        print(f"FATAL: {e.args[0]}", file=sys.stderr)
        return 3
    Path(a.out).write_text(out, encoding="utf-8", newline="\n")
    print(f"OK: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
