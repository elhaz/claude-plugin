#!/usr/bin/env python3
"""역산 DCF — 현재 주가가 요구하는 성장률을 구하고 투자원칙 v2 의 사유형/적정가형 판정을 낸다.

모델 (투자원칙 v2 2절 예시와 같음):
    주가 = Σ_{t=1..N} F·(1+g)^t / (1+r)^t  +  M·F·(1+g)^N / (1+r)^N
    F = 주당 현금흐름(FCF, 없으면 EPS), r = 할인율, N = 성장 기간, M = 성장 후 평가 배수

판정 (v2): 요구 ≤ 실제 → 사유형 / 요구 > 실제×1.5 이고 차이 ≥ 5%p → 적정가형 / 그 사이 → 사유형(경계)
F ≤ 0 이면 계산 불가 → 재료형 또는 적정가형은 사건·매출 기준으로 따로 판단한다.

사용:
    python3 reverse_dcf.py --price 148.01 --per-share 1.0 --actual-growth 15
    python3 reverse_dcf.py --price 100 --per-share 1 --actual-growth 15 --json
"""

from __future__ import annotations

import argparse
import json
import sys

RATIO = 1.5      # 적정가형: 요구 성장률이 실제의 1.5배 초과
GAP_PP = 5.0     # 그리고 차이 5%p 이상


def price_for(g: float, f: float, r: float, n: int, m: float) -> float:
    """성장률 g 일 때의 이론 주가."""
    pv = sum(f * (1 + g) ** t / (1 + r) ** t for t in range(1, n + 1))
    return pv + m * f * (1 + g) ** n / (1 + r) ** n


def required_growth(price: float, f: float, r: float = 0.10, n: int = 10, m: float = 15.0) -> float | None:
    """price 를 정당화하는 연 성장률(소수). f ≤ 0 이면 None."""
    if f <= 0 or price <= 0:
        return None
    lo, hi = -0.9, 5.0
    if price_for(hi, f, r, n, m) < price:
        return hi                         # 500% 로도 모자람 — 사실상 무한 기대
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if price_for(mid, f, r, n, m) < price else (lo, mid)
    return (lo + hi) / 2


def judge(req_pct: float | None, actual_pct: float | None) -> dict:
    """v2 규칙으로 판정. 퍼센트 단위 입력."""
    if req_pct is None:
        return {"verdict": "계산 불가", "note": "현금흐름·이익이 0 이하 — 재료형/적정가형을 사건·매출 기준으로 판단"}
    if actual_pct is None:
        return {"verdict": "판정 보류", "note": "실제 성장률이 없어 비교 불가"}
    gap = req_pct - actual_pct
    ratio = req_pct / actual_pct if actual_pct > 0 else float("inf")
    if req_pct <= actual_pct:
        verdict, note = "사유형", "요구 성장률이 실제 이하 — 실적만큼 또는 싸게 거래"
    elif ratio > RATIO and gap >= GAP_PP:
        verdict, note = "적정가형", f"요구가 실제의 {RATIO}배 초과이고 차이 {GAP_PP}%p 이상"
    else:
        verdict, note = "사유형", "요구가 실제보다 높지만 기준 미달 — 경계선"
    return {"verdict": verdict, "ratio": None if ratio == float("inf") else round(ratio, 2),
            "gap_pp": round(gap, 1), "note": note}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--price", type=float, required=True, help="현재 주가")
    ap.add_argument("--per-share", type=float, required=True, help="주당 FCF (없으면 EPS)")
    ap.add_argument("--actual-growth", type=float, help="실제 성장률 %% (최근 3년 평균 또는 컨센서스)")
    ap.add_argument("--discount", type=float, default=10.0, help="할인율 %% (기본 10)")
    ap.add_argument("--years", type=int, default=10, help="성장 기간 (기본 10년)")
    ap.add_argument("--terminal", type=float, default=15.0, help="성장 후 평가 배수 (기본 15)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    g = required_growth(a.price, a.per_share, a.discount / 100, a.years, a.terminal)
    req_pct = None if g is None else round(g * 100, 1)
    out = {"required_growth_pct": req_pct, "actual_growth_pct": a.actual_growth,
           "assumptions": {"discount_pct": a.discount, "years": a.years, "terminal_multiple": a.terminal},
           **judge(req_pct, a.actual_growth)}
    if a.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"요구 성장률 {req_pct}% · 실제 {a.actual_growth}% → {out['verdict']} ({out['note']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
