#!/usr/bin/env python3
"""findata(fdp) 종목 기초 데이터를 stock-data-collector 출력 양식의 짧은 표로 바꾼다.

fdp `GET /api/fundamentals/{ticker}` 원본은 종목당 30~60KB 라 에이전트가 직접 읽으면 비싸다.
이 스크립트가 필요한 값만 골라 계산식이 정해진 지표(P/S·FCF Yield·연도별 배수 등)를 붙여 낸다.
없는 종목은 write 키가 있으면 `POST /api/collect/fundamentals` 로 수집시킨 뒤 다시 조회한다.

사용:
    python3 fdp_fundamentals.py GOOGL --peers MSFT,META,AMZN --reason "종목 분석"
    python3 fdp_fundamentals.py gap --ticker GOOGL --topic "equity short interest" --reason "공매도 비율 웹 보충"

주소: --api-base → $FDP_API_BASE → http://localhost:8000(응답 시) → https://findata.xhhan.com
키:   $FDP_API_KEY → $FDP_REPORTER_API_KEY → ~/.config/financial-data-platform/api.env
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path

PUBLIC_BASE = "https://findata.xhhan.com"
LOCAL_BASE = "http://localhost:8000"
UA = "stock-analysis-fdp/1.0"   # Cloudflare 가 기본 UA 를 막는다
REQUESTER = "stock-analysis:collector"
DEFAULT_PURPOSE = "종목 데이터 수집"   # --reason 없을 때 (직접 실행 등)
REASON_MAX = 200                      # fdp collect reason 칸 최대 길이

# 수집 에이전트가 웹으로 채워야 하는 항목 — fdp 에 수집기가 없는 것
WEB_ONLY = [
    "Business Model / Revenue Breakdown (세그먼트·지역)",
    "Short Float % (유동주식 기준 — fdp 는 잔고·Days to Cover·발행주식 대비만)",
    "Analyst 최근 목표가 변동 · Buy/Hold/Sell 수",
    "Non-GAAP EPS (회사가 발표하는 경우)",
    "Recent Events (실적 헤드라인·가이던스·뉴스)",
    "Institutional 주요 변동",
    "업종 KPI (리츠 FFO/AFFO·BDC NAV·SaaS NRR 등, sector-metrics-guide)",
]


def collect_reason(purpose: str | None, main: str, chunk: list[str]) -> str:
    """fdp 수집 요청의 reason — 요청자는 API 키로 구분되니 '왜' 만 적는다.

    예: "종목 분석 GOOGL", "업데이트 GOOGL · 경쟁사 비교". 목적에 티커가 이미 있으면 붙이지 않는다.
    """
    purpose = " ".join((purpose or "").split()) or DEFAULT_PURPOSE
    text = purpose if main in purpose.upper().split() else f"{purpose} {main}"
    if main not in chunk:
        text += " · 경쟁사 비교"
    return text[:REASON_MAX]


# ---------- HTTP ----------

def _key() -> str | None:
    for name in ("FDP_API_KEY", "FDP_REPORTER_API_KEY"):
        if os.getenv(name):
            return os.environ[name]
    f = Path.home() / ".config/financial-data-platform/api.env"
    try:
        for line in f.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            if k.strip() in ("FDP_API_KEY", "FDP_REPORTER_API_KEY") and v.strip():
                return v.strip()
    except OSError:
        pass
    return None


def _request(url: str, method: str = "GET", body: dict | None = None, key: str | None = None, timeout: float = 30):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    if key:
        headers["X-API-Key"] = key
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8") or "null")
        except ValueError:
            return e.code, None


def resolve_base(explicit: str | None) -> str:
    for cand in (explicit, os.getenv("FDP_API_BASE")):
        if cand:
            return cand.rstrip("/")
    try:
        status, _ = _request(f"{LOCAL_BASE}/api/health", timeout=2)
        if status == 200:
            return LOCAL_BASE
    except (urllib.error.URLError, OSError, ValueError):
        pass
    return PUBLIC_BASE


class Fdp:
    def __init__(self, base: str):
        self.base = base
        self.key = _key()

    def get(self, path: str, **query):
        q = urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})
        return _request(f"{self.base}{path}" + (f"?{q}" if q else ""))

    def post(self, path: str, body: dict | None = None, **query):
        q = urllib.parse.urlencode(query)
        return _request(f"{self.base}{path}" + (f"?{q}" if q else ""), "POST", body, self.key, timeout=180)

    def fundamentals(self, tickers: list[str], collect: bool = True, purpose: str | None = None) -> tuple[dict, list[str]]:
        """{ticker: 응답}, 수집 트리거 메모. 404 는 키가 있으면 한 번에 수집 후 재조회.

        tickers[0] 이 본 종목, 나머지는 경쟁사. purpose 는 수집 요청 reason 의 앞머리.
        """
        got, missing, notes = {}, [], []
        for t in tickers:
            status, body = self.get(f"/api/fundamentals/{t}", insider_days=180)
            if status == 200:
                got[t] = body
            else:
                missing.append(t)
        if missing and collect:
            if not self.key:
                notes.append(f"fdp 에 없음 · write 키 없어 수집 못 함: {', '.join(missing)}")
            else:
                for i in range(0, len(missing), 10):     # API 한 번에 최대 10개
                    chunk = missing[i:i + 10]
                    status, _ = self.post("/api/collect/fundamentals", ticker=",".join(chunk),
                                          reason=collect_reason(purpose, tickers[0], chunk))
                    notes.append(f"수집 요청 {','.join(chunk)} → HTTP {status}")
                for t in list(missing):
                    status, body = self.get(f"/api/fundamentals/{t}", insider_days=180)
                    if status == 200:
                        got[t] = body
                        missing.remove(t)
                if missing:
                    notes.append(f"수집 후에도 없음(ETF·비상장·외국 코드 등): {', '.join(missing)}")
        return got, notes

    def prices(self, symbol: str, start: str) -> list[tuple[str, float]]:
        status, body = self.get(f"/api/prices/{symbol}", start_date=start, limit=5000)   # 기본 500행은 최근분만
        if status != 200 or not body:
            return []
        cols = body["columns"]
        di, ci = cols.index("date"), cols.index("close")
        return [(r[di], r[ci]) for r in body["data"] if r[ci] is not None]


# ---------- 표 가공 ----------

def statement(fund: dict, kind: str, period: str) -> tuple[list[str], dict[str, list]]:
    """(기간 열, {항목: 값 목록}) — 열은 최신이 앞."""
    s = ((fund.get("financials") or {}).get(kind) or {}).get(period)
    if not s:
        return [], {}
    return s["columns"][1:], {row[0]: row[1:] for row in s["data"]}


def pick(rows: dict, *names: str) -> list:
    for n in names:
        if n in rows and any(v is not None for v in rows[n]):
            return rows[n]
    return []


def at(vals: list, i: int):
    return vals[i] if i < len(vals) else None


def ttm(vals: list):
    xs = vals[:4]
    return sum(xs) if len(xs) == 4 and all(v is not None for v in xs) else None


def div(a, b):
    return a / b if a is not None and b not in (None, 0) else None


def money(v, cur: str = "USD") -> str:
    if v is None:
        return "—"
    sign = "-" if v < 0 else ""
    v = abs(v)
    sym = "$" if cur == "USD" else ""
    for unit, n in (("T", 1e12), ("B", 1e9), ("M", 1e6)):
        if v >= n:
            return f"{sign}{sym}{v / n:,.2f}{unit}"
    return f"{sign}{sym}{v:,.0f}"


def num(v, nd: int = 2, suffix: str = "") -> str:
    return "—" if v is None else f"{v:,.{nd}f}{suffix}"


def pct(v, nd: int = 1) -> str:
    """소수 비율 → %."""
    return "—" if v is None else f"{v * 100:,.{nd}f}%"


def close_on(prices: list[tuple[str, float]], day: str):
    """day 이전 마지막 종가."""
    last = None
    for d, c in prices:
        if d > day:
            break
        last = c
    return last


def valuation_history(fund: dict, prices: list[tuple[str, float]]) -> list[tuple]:
    cols, inc = statement(fund, "income", "annual")
    bcols, bal = statement(fund, "balance", "annual")
    rev = pick(inc, "total_revenue", "operating_revenue")
    eps = pick(inc, "diluted_earnings_per_share", "basic_earnings_per_share")
    shares = pick(inc, "weighted_average_diluted_shares_outstanding", "weighted_average_basic_shares_outstanding")
    ebitda = pick(inc, "ebitda", "normalized_ebitda")
    bidx = {c: i for i, c in enumerate(bcols)}
    equity = pick(bal, "common_stock_equity", "total_common_equity")
    debt = pick(bal, "total_debt")
    ltd = pick(bal, "long_term_debt_and_capital_lease_obligation", "long_term_debt")
    std = pick(bal, "current_debt_and_capital_lease_obligation", "current_debt")
    cash = pick(bal, "cash_cash_equivalents_and_short_term_investments", "cash_and_cash_equivalents")
    out = []
    for i, c in enumerate(cols):
        px, sh = close_on(prices, c), at(shares, i)
        j = bidx.get(c)
        eq = at(equity, j) if j is not None else None
        d = at(debt, j) if j is not None else None
        if d is None and j is not None and (at(ltd, j) is not None or at(std, j) is not None):
            d = (at(ltd, j) or 0) + (at(std, j) or 0)
        ca = at(cash, j) if j is not None else None
        mcap = px * sh if px is not None and sh else None
        ev = mcap + (d or 0) - (ca or 0) if mcap is not None else None
        e = at(eps, i)
        out.append((c[:4], px, div(px, e) if e and e > 0 else None, div(ev, at(rev, i)),
                    div(ev, at(ebitda, i)) if (at(ebitda, i) or 0) > 0 else None, div(mcap, eq) if (eq or 0) > 0 else None))
    return out


def short_summary(fund: dict, shares: float | None) -> list[str]:
    """FINRA 공매도 잔고(월 2회)·일별 공매도 거래량 비율 (fdp #161)."""
    sh = fund.get("short") or {}
    rows = (sh.get("interest") or {}).get("data") or []
    if not rows:
        return ["- fdp 공매도 데이터 없음"]
    cols = sh["interest"]["columns"]
    ix = {c: i for i, c in enumerate(cols)}
    last = rows[-1]
    si = last[ix["short_interest"]]
    lines = [f"- 잔고 {last[ix['date']]} 결제일: {money(si, '')}주 (직전 대비 {num(last[ix['change_pct']], 2, '%')}) · "
             f"Days to Cover {num(last[ix['days_to_cover']])} · 평균 거래량 {money(last[ix['avg_daily_volume']], '')}주"
             + (f" · 발행주식 대비 {pct(div(si, shares))}" if shares else "")]
    if len(rows) > 1:
        lines.append("- 이전: " + " · ".join(f"{r[ix['date']]} {money(r[ix['short_interest']], '')}주" for r in rows[:-1]))
    if sh.get("ratio_5d") is not None:
        lines.append(f"- 일별 공매도 거래량 비율 최근 {sh.get('ratio_days')}일 평균 {pct(sh['ratio_5d'])} "
                     f"({sh.get('ratio_as_of')}까지, FINRA 장외 보고분 기준 — 거래소 전체 아님)")
    return lines


def insider_summary(fund: dict) -> list[str]:
    ins = fund.get("insider") or {}
    cols, rows = ins.get("columns") or [], ins.get("data") or []
    if not rows:
        return ["- 최근 180일 Form 4 없음 (외국 발행사는 Form 4 대상 아님)"]
    ix = {c: i for i, c in enumerate(cols)}
    buys = [r for r in rows if r[ix["code"]] == "P"]
    sells = [r for r in rows if r[ix["code"]] == "S"]
    val = lambda rs: sum(r[ix["value"]] or 0 for r in rs)
    plan = [r for r in sells if r[ix["is_10b5_1"]] is True]
    unknown = [r for r in sells if r[ix["is_10b5_1"]] is None]
    lines = [
        f"- 최근 {ins.get('days', 180)}일: 장내 매수 {len(buys)}건 {money(val(buys))} · "
        f"장내 매도 {len(sells)}건 {money(val(sells))} · 기타(보상·행사·세금) {len(rows) - len(buys) - len(sells)}건",
        f"- 매도 중 10b5-1 계획 매도 {len(plan)}건 {money(val(plan))}"
        + (f" · 양식상 미상 {len(unknown)}건" if unknown else ""),
    ]
    by = {}
    for r in sells:
        k = (r[ix["insider"]], r[ix["title"]])
        by[k] = by.get(k, 0) + (r[ix["value"]] or 0)
    top = sorted(by.items(), key=lambda kv: -kv[1])[:3]
    if top:
        lines.append("- 매도 상위: " + " · ".join(f"{n}{f' ({t})' if t else ''} {money(v)}" for (n, t), v in top))
    if buys:
        lines.append("- 장내 매수: " + " · ".join(
            f"{r[ix['trade_date']]} {r[ix['insider']]} {money(r[ix['value']])}" for r in buys[:5]))
    return lines


def peer_row(t: str, f: dict) -> str:
    m = f.get("metrics") or {}
    cur = m.get("currency") or "USD"
    return (f"| {t} | {money(m.get('market_cap'), cur)} | {pct(m.get('revenue_growth'))} | {num(m.get('forward_pe'), 1)} | "
            f"{num(m.get('enterprise_to_revenue'), 1)} | {pct(m.get('gross_margin'))} | {pct(m.get('operating_margin'))} |")


def render(t: str, f: dict, peers: dict, fdp: Fdp, notes: list[str]) -> str:
    m, c = f.get("metrics") or {}, f.get("consensus") or {}
    cur = m.get("currency") or c.get("currency") or "USD"
    price = c.get("current_price")
    qcols, qinc = statement(f, "income", "quarter")
    _, qcash = statement(f, "cash", "quarter")
    _, qbal = statement(f, "balance", "quarter")
    acols, ainc = statement(f, "income", "annual")
    _, acash = statement(f, "cash", "annual")

    qrev = pick(qinc, "total_revenue", "operating_revenue")
    fcf_ttm = ttm(pick(qcash, "free_cash_flow"))
    rev_ttm = ttm(qrev)
    mcap = m.get("market_cap")
    fwd = {e["period"]: e for e in (f.get("estimates") or {}).get("eps", [])}
    fwd_rev = {e["period"]: e for e in (f.get("estimates") or {}).get("revenue", [])}

    start = min([c_ for c_ in acols] + [(date.today() - timedelta(days=370)).isoformat()])
    prices = fdp.prices(t, (date.fromisoformat(start[:10]) - timedelta(days=10)).isoformat())
    year = [p for d, p in prices if d >= (date.today() - timedelta(days=365)).isoformat()]

    L = [f"## Data Collection: {t} (findata)", "",
         f"> 출처: findata {fdp.base} · 기초 데이터 기준일 {f.get('as_of')} ({f.get('age_days')}일 전"
         f"{', 오래됨' if f.get('stale') else ''}) · 원천 {f.get('source')}. 아래 표는 그대로 쓰고 다시 검색하지 않는다.", ""]

    L += ["### Basic Info",
          f"- Price: {num(price)} {cur} / Market Cap: {money(mcap, cur)} / EV: {money(m.get('enterprise_value'), cur)}",
          f"- 52W Range: {num(min(year)) if year else '—'} ~ {num(max(year)) if year else '—'} (fdp 종가 기준) / "
          f"1Y 수익률: {pct(m.get('price_return_1y'))}",
          f"- Shares Outstanding(≈시총/주가): {money(div(mcap, price), '')} / Beta: {num(m.get('beta'))} / "
          f"Div Yield: {num(m.get('dividend_yield'), 2, '%')} / Payout: {pct(m.get('payout_ratio'))}", ""]

    fy0 = fwd.get("0y") or {}
    fy1 = fwd.get("+1y") or {}
    L += ["### Valuation Set", "| Metric | Value |", "|---|---|",
          f"| P/E (TTM) | {num(m.get('pe_ratio'), 1)} |",
          f"| Forward P/E | {num(m.get('forward_pe'), 1)} |",
          f"| PEG | {num(m.get('peg_ratio'))} |",
          f"| P/S (TTM) | {num(div(mcap, rev_ttm))} |",
          f"| P/B | {num(m.get('price_to_book'))} |",
          f"| EV/EBITDA | {num(m.get('enterprise_to_ebitda'), 1)} |",
          f"| EV/Sales | {num(m.get('enterprise_to_revenue'))} |",
          f"| FCF Yield (TTM) | {pct(div(fcf_ttm, mcap))} |",
          f"| Beta | {num(m.get('beta'))} |",
          f"| Div Yield | {num(m.get('dividend_yield'), 2, '%')} |",
          f"| Forward EPS (올해 / 내년) | {num(fy0.get('avg'))} / {num(fy1.get('avg'))} |", ""]

    if fwd:
        L += ["### Estimates (컨센서스)", "| 기간 | EPS 평균 (저~고) | 전년 EPS | EPS 성장 | 매출 평균 | 매출 성장 | 애널리스트 수 |",
              "|---|---|---|---|---|---|---|"]
        for p in ("0q", "+1q", "0y", "+1y"):
            e, r = fwd.get(p) or {}, fwd_rev.get(p) or {}
            if e or r:
                L.append(f"| {p} | {num(e.get('avg'))} ({num(e.get('low'))}~{num(e.get('high'))}) | {num(e.get('yearAgoEps'))} | "
                         f"{pct(e.get('growth'))} | {money(r.get('avg'), cur)} | {pct(r.get('growth'))} | {e.get('numberOfAnalysts', '—')} |")
        L.append("")

    if qcols:
        op, eps, ebitda, ni = (pick(qinc, "operating_income", "total_operating_income_as_reported"),
                               pick(qinc, "diluted_earnings_per_share", "basic_earnings_per_share"),
                               pick(qinc, "ebitda", "normalized_ebitda"), pick(qinc, "net_income", "net_income_common_stockholders"))
        gp = pick(qinc, "gross_profit")
        L += ["### Quarterly Financials (GAAP)", "| Quarter | Revenue | Op Income | Net Income | EPS (GAAP 희석) | EBITDA | GM | FCF |",
              "|---|---|---|---|---|---|---|---|"]
        qfcf = pick(qcash, "free_cash_flow")
        for i, q in enumerate(qcols):
            L.append(f"| {q} | {money(at(qrev, i), cur)} | {money(at(op, i), cur)} | {money(at(ni, i), cur)} | {num(at(eps, i))} | "
                     f"{money(at(ebitda, i), cur)} | {pct(div(at(gp, i), at(qrev, i)))} | {money(at(qfcf, i), cur)} |")
        L.append("")

    if acols:
        arev, ani = pick(ainc, "total_revenue", "operating_revenue"), pick(ainc, "net_income", "net_income_common_stockholders")
        aeps, afcf = pick(ainc, "diluted_earnings_per_share", "basic_earnings_per_share"), pick(acash, "free_cash_flow")
        L += ["### Annual Financials", "| FY | Revenue | YoY | Net Income | EPS (GAAP 희석) | FCF |", "|---|---|---|---|---|---|"]
        for i, y in enumerate(acols):
            if at(arev, i) is None and at(ani, i) is None:
                continue
            prev = at(arev, i + 1)
            yoy = div(at(arev, i) - prev, prev) if at(arev, i) is not None and prev else None
            L.append(f"| {y[:4]} | {money(at(arev, i), cur)} | {pct(yoy)} | {money(at(ani, i), cur)} | {num(at(aeps, i))} | {money(at(afcf, i), cur)} |")
        L.append("")
        L += ["### Valuation History (회계연도 말 종가 × 연간 재무로 계산)", "| Year | 종가 | P/E | EV/Rev | EV/EBITDA | P/B |",
              "|---|---|---|---|---|---|"]
        for y, px, pe, evr, eve, pb in valuation_history(f, prices):
            if pe is None and evr is None and pb is None:
                continue
            L.append(f"| {y} | {num(px)} | {num(pe, 1)} | {num(evr, 1)} | {num(eve, 1)} | {num(pb, 1)} |")
        L.append("")

    if peers:
        L += ["### Peer Comparison", "| Company | Mkt Cap | Rev Growth | Fwd P/E | EV/Sales | GM | Op Margin |", "|---|---|---|---|---|---|---|",
              peer_row(t, f)]
        L += [peer_row(p, pf) for p, pf in peers.items()]
        L.append("")

    debt_q = pick(qbal, "total_debt")
    cash_q = pick(qbal, "cash_cash_equivalents_and_short_term_investments", "cash_and_cash_equivalents")
    net_debt = at(debt_q, 0) - at(cash_q, 0) if at(debt_q, 0) is not None and at(cash_q, 0) is not None else None
    L += ["### Financial Health", "| Metric | Value |", "|---|---|",
          f"| Current Ratio | {num(m.get('current_ratio'))} |",
          f"| Quick Ratio | {num(m.get('quick_ratio'))} |",
          f"| Debt/Equity | {num(m.get('debt_to_equity'), 1, '%')} |",
          f"| 순차입금 (최근 분기, 음수=순현금) | {money(net_debt, cur)} |",
          f"| FCF (TTM) | {money(fcf_ttm, cur)} |",
          f"| ROE / ROA | {pct(m.get('return_on_equity'))} / {pct(m.get('return_on_assets'))} |",
          f"| 마진 (Gross / Op / Net) | {pct(m.get('gross_margin'))} / {pct(m.get('operating_margin'))} / {pct(m.get('profit_margin'))} |", ""]

    if c:
        L += ["### Analyst Consensus",
              f"- Rating: {c.get('recommendation', '—')} (평균 {num(c.get('recommendation_mean'))}, 1=강력매수 5=매도) · "
              f"애널리스트 {c.get('number_of_analysts', '—')}명",
              f"- Target Avg: {num(c.get('target_consensus'))} / Median: {num(c.get('target_median'))} / "
              f"High: {num(c.get('target_high'))} / Low: {num(c.get('target_low'))} · "
              f"현재가 대비 {pct(div((c.get('target_consensus') or 0) - (price or 0), price))}", ""]

    L += ["### Insider (SEC Form 4)"] + insider_summary(f) + [""]
    L += ["### Short Interest (FINRA)"] + short_summary(f, div(mcap, price)) + [""]

    missing = f.get("missing") or []
    L += ["### fdp 상태"]
    L += [f"- {n}" for n in notes]
    if missing:
        L.append(f"- fdp 응답의 missing: {', '.join(missing)}")
    L.append("- **웹으로 채울 것**: " + " / ".join(WEB_ONLY) + (" / " + ", ".join(missing) if missing else ""))
    return "\n".join(L)


# ---------- CLI ----------

def cmd_gap(args, fdp: Fdp) -> int:
    body = {"topic": args.topic, "category": args.category, "requester": REQUESTER,
            "context": args.ticker, "reason": args.reason}
    if not fdp.key:
        print("data_gaps: 키 없음 — 기록 생략")
        return 0
    status, _ = fdp.post("/api/meta/data-gaps", body)
    print(f"data_gaps: {args.ticker} {args.topic} → HTTP {status}")
    return 0 if status in (200, 201) else 1


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # Windows cp949 콘솔
    except (AttributeError, ValueError):
        pass
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["gap"]:
        ap = argparse.ArgumentParser(prog="fdp_fundamentals.py gap", description="웹으로 보충한 항목을 fdp data_gaps 에 기록")
        ap.add_argument("--ticker", required=True)
        ap.add_argument("--topic", required=True)
        ap.add_argument("--reason", default=None)
        ap.add_argument("--category", default="equity")
        ap.add_argument("--api-base", default=None)
        args = ap.parse_args(argv[1:])
        return cmd_gap(args, Fdp(resolve_base(args.api_base)))

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("ticker")
    ap.add_argument("--peers", default="", help="쉼표 구분 경쟁사 티커 (최대 10)")
    ap.add_argument("--no-collect", action="store_true", help="없는 종목을 수집 요청하지 않는다")
    ap.add_argument("--reason", default=None,
                    help='수집 요청 이유(fdp 활동 기록의 "왜"). 예: "종목 분석", "업데이트". 티커는 자동으로 붙는다')
    ap.add_argument("--api-base", default=None)
    args = ap.parse_args(argv)

    t = args.ticker.upper()
    if t.isdigit():
        print(f"## Data Collection: {t} (findata)\n\n- fdp 는 한국 종목 기초 데이터를 수집하지 않는다 — 전 항목 웹 수집")
        return 2
    fdp = Fdp(resolve_base(args.api_base))
    peers = [p.strip().upper() for p in args.peers.split(",") if p.strip() and p.strip().upper() != t][:10]
    try:
        got, notes = fdp.fundamentals([t] + peers, collect=not args.no_collect, purpose=args.reason)
    except (urllib.error.URLError, OSError) as e:
        print(f"## Data Collection: {t} (findata)\n\n- fdp 접속 실패({fdp.base}): {e} — 전 항목 웹 수집")
        return 2
    if t not in got:
        print(f"## Data Collection: {t} (findata)\n\n" + "\n".join(f"- {n}" for n in notes) + "\n- 전 항목 웹 수집")
        return 2
    print(render(t, got[t], {p: got[p] for p in peers if p in got}, fdp, notes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
