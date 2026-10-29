"""레인 그림 틀 — JSON 명세를 diagram-design 형식의 HTML(SVG 한 장)로 만든다.

한 줄(레인) = 한 메뉴, 상자 = 업무 하나, 맨 위 띠 = 요청 묶음, 왼쪽에서 오른쪽 = 일이 거치는 순서.
선은 자동으로 꺾어 그리는 틀이다. 겹치면 명세의 from_dx · to_dx · label_dx · label_dy 로 비켜 놓는다.
PNG 는 diagram-design 플러그인의 export-diagram 이나 볼트의 래스터 스크립트로 뽑는다.

사용:
    python lane_diagram.py lane_spec.json -o 05_Attachments/첨부파일/이름.dd.html

명세 예: ../examples/lane_spec_example.json
"""

import argparse
import html
import json
import sys
from pathlib import Path

FONT = "'Geist', 'Noto Sans KR', 'Malgun Gothic', sans-serif"
MONO = "'Geist Mono', monospace"
INK, MUTED, SOFT, ACC, PAPER, LINK = "#2d3142", "#4f5d75", "#5a6580", "#bf4520", "#f5f5f5", "#2e5aa8"
W, H = 132, 56          # 상자 크기 (한글 12px 라벨 기준)
COL0, COL_GAP = 176, 148
LANE_Y0, LANE_H = 116, 80

STYLE = {
    "main": (MUTED, "arrow", False),
    "back": (MUTED, "arrow", True),
    "link": (LINK, "arrow-link", False),
    "focus": (ACC, "arrow-accent", False),
    "focus-dash": (ACC, "arrow-accent", True),
}
LEGEND = {
    "main": "일 흐름",
    "back": "되돌림 · 순서 정보",
    "link": "입력 · 판정",
    "focus": "핵심 고리",
}


def esc(s):
    return html.escape(str(s), quote=False)


def label_w(s):
    w = 0.0
    for ch in str(s):
        w += 12 if ord(ch) >= 0x1100 else 12 * 0.6
    return int((w + 16 + 3) // 4 * 4)


def text(x, y, s, fill, size=12, weight=500, family=FONT, anchor="middle", extra=""):
    return (f'<text x="{x:.0f}" y="{y:.0f}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'font-family="{family}" text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def mask_label(cx, top, s, fill):
    lw = label_w(s)
    return [f'<rect x="{cx - lw / 2:.0f}" y="{top:.0f}" width="{lw}" height="16" rx="2" fill="{PAPER}"/>',
            text(cx, top + 12, s, fill)]


class Layout:
    def __init__(self, spec):
        self.lanes = spec["lanes"]
        self.lane_y = {ln["key"]: LANE_Y0 + i * LANE_H for i, ln in enumerate(self.lanes)}
        self.nodes = {n["id"]: n for n in spec["nodes"]}
        bad = [n["id"] for n in spec["nodes"] if n["lane"] not in self.lane_y]
        if bad:
            raise ValueError("없는 레인을 쓴 상자: " + ", ".join(bad))
        max_col = max([n["col"] for n in spec["nodes"]] + [s.get("to", 0) for s in spec.get("stages", [])])
        self.vw = COL0 + (max_col + 1) * COL_GAP + 40
        self.top = 24
        self.bot = LANE_Y0 + len(self.lanes) * LANE_H + 16

    def x(self, col):
        return COL0 + col * COL_GAP

    def pos(self, nid):
        n = self.nodes[nid]
        return self.x(n["col"]), self.lane_y[n["lane"]] + 12

    def L(self, n): return self.pos(n)[0]
    def R(self, n): return self.pos(n)[0] + W
    def T(self, n): return self.pos(n)[1]
    def B(self, n): return self.pos(n)[1] + H
    def CX(self, n): return self.pos(n)[0] + W / 2
    def CY(self, n): return self.pos(n)[1] + H / 2


def edge_path(lay, e):
    a, b = e["from"], e["to"]
    fdx, tdx = e.get("from_dx", 0), e.get("to_dx", 0)
    ya, yb = lay.T(a), lay.T(b)
    ca, cb = lay.nodes[a]["col"], lay.nodes[b]["col"]
    r = 8
    if ya == yb:
        if cb > ca:  # 같은 줄 앞으로
            d = f"M {lay.R(a)},{lay.CY(a)} L {lay.L(b)},{lay.CY(b)}"
            lab = ((lay.R(a) + lay.L(b)) / 2, lay.CY(a) - 22)
        else:  # 같은 줄 뒤로: 상자 아래로 돌아간다
            y = lay.B(a) + 10
            x1, x2 = lay.CX(a) + fdx, lay.CX(b) + tdx
            d = f"M {x1},{lay.B(a)} V {y} H {x2} V {lay.B(b)}"
            lab = ((x1 + x2) / 2, y - 4)
        return d, lab
    down = yb > ya
    if ca == cb:  # 같은 열 위아래
        x = lay.CX(a) + fdx
        d = f"M {x},{lay.B(a) if down else lay.T(a)} L {x},{lay.T(b) if down else lay.B(b)}"
        lab = (x, (lay.B(a) + lay.T(b)) / 2 - 8 if down else (lay.T(a) + lay.B(b)) / 2 - 8)
        return d, lab
    route = e.get("route", "hv" if cb > ca else "vh")
    if route == "hv":  # 옆으로 나가 대상 위(아래)로 들어간다
        x2 = lay.CX(b) + tdx
        y1 = lay.CY(a)
        s = 1 if x2 > lay.R(a) else -1
        x1 = lay.R(a) if s > 0 else lay.L(a)
        end = lay.T(b) if down else lay.B(b)
        v = 1 if down else -1
        d = f"M {x1},{y1} H {x2 - s * r} Q {x2},{y1} {x2},{y1 + v * r} V {end}"
        lab = (x2, (lay.lane_y[lay.nodes[b]["lane"]] - 8) if down else end + 4)
        return d, lab
    # vh: 위(아래)로 나가 대상 옆으로 들어간다
    x1 = lay.CX(a) + fdx
    y2 = lay.CY(b)
    s = 1 if lay.R(b) < x1 else -1
    x2 = lay.R(b) if s > 0 else lay.L(b)
    start = lay.B(a) if down else lay.T(a)
    v = 1 if down else -1
    d = f"M {x1},{start} V {y2 - v * r} Q {x1},{y2} {x1 - s * r},{y2} H {x2}"
    lab = ((x1 + x2) / 2, y2 - 22)
    return d, lab


def render(spec):
    lay = Layout(spec)
    vw = lay.vw
    out = []
    head = spec.get("caption", "한 줄 = 한 메뉴, 상자 = 업무 하나, 맨 위 띠 = 요청 묶음, 왼쪽에서 오른쪽 = 일이 거치는 순서")
    lw = label_w(head)
    out.append(f'<rect x="40" y="{lay.top}" width="{vw - 80}" height="{lay.bot - lay.top}" rx="8" fill="rgba(45,49,66,0.02)" stroke="rgba(45,49,66,0.14)" stroke-width="0.8"/>')
    out.append(f'<rect x="168" y="{lay.top + 4}" width="{lw}" height="16" rx="2" fill="{PAPER}"/>')
    out.append(text(168 + lw / 2, lay.top + 16, head, "rgba(45,49,66,0.60)"))
    for i, ln in enumerate(lay.lanes):
        y = lay.lane_y[ln["key"]]
        if i > 0:
            out.append(f'<line x1="48" y1="{y}" x2="{vw - 48}" y2="{y}" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>')
        out.append(text(56, y + 38, ln["name"], INK, weight=600, anchor="start"))
        if ln.get("code"):
            out.append(text(56, y + 54, ln["code"], SOFT, anchor="start"))
    if spec.get("stages"):
        out.append(text(56, 68, spec.get("stage_title", "요청 묶음"), SOFT, anchor="start"))
    for st in spec.get("stages", []):
        x1, x2 = lay.x(st["from"]), lay.x(st["to"]) + W
        if st.get("now"):
            out.append(f'<rect x="{x1}" y="52" width="{x2 - x1}" height="24" rx="4" fill="transparent" stroke="rgba(45,49,66,0.18)" stroke-width="0.8" stroke-dasharray="4,3"/>')
            out.append(text((x1 + x2) / 2, 69, st["label"], SOFT))
        else:
            out.append(f'<rect x="{x1}" y="52" width="{x2 - x1}" height="24" rx="4" fill="rgba(45,49,66,0.06)" stroke="rgba(45,49,66,0.18)" stroke-width="0.8"/>')
            out.append(text((x1 + x2) / 2, 69, st["label"], INK, weight=600))
    if spec.get("note"):
        out.append(text(lay.x(0), 97, spec["note"], SOFT, anchor="start"))

    # 선을 상자보다 먼저 그린다 (상자가 선을 덮는다)
    used = []
    for e in spec.get("edges", []):
        for k in ("from", "to"):
            if e[k] not in lay.nodes:
                raise ValueError(f"없는 상자를 잇는 선: {e['from']} -> {e['to']}")
        color, marker, dashed = STYLE[e.get("style", "main")]
        if e.get("dashed") is not None:
            dashed = e["dashed"]
        used.append(e.get("style", "main"))
        d, (lx, ly) = edge_path(lay, e)
        da = ' stroke-dasharray="4,3"' if dashed else ""
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="1.2"{da} marker-end="url(#{marker})"/>')
        if e.get("label"):
            out += mask_label(lx + e.get("label_dx", 0), ly + e.get("label_dy", 0), e["label"], SOFT if color == MUTED else color)
    for t in spec.get("texts", []):
        y = lay.lane_y[t["lane"]] + t.get("dy", 36)
        out.append(text(lay.x(t.get("col", 0)), y, t["text"], SOFT, anchor="start"))

    sty = {
        "new": ("#ffffff", INK, "rgba(45,49,66,0.40)", "rgba(45,49,66,0.8)"),
        "now": ("rgba(45,49,66,0.03)", "rgba(45,49,66,0.30)", "rgba(45,49,66,0.30)", "rgba(45,49,66,0.7)"),
    }
    for n in spec["nodes"]:
        x, y = lay.pos(n["id"])
        fill, stroke, tstroke, tfill = sty[n.get("kind", "new")]
        cx = x + W / 2
        out.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="6" fill="{PAPER}"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1"/>')
        if n.get("tag"):
            tw = max(28, int(len(n["tag"]) * 5.2) + 10)
            out.append(f'<rect x="{x + 8}" y="{y + 6}" width="{tw}" height="12" rx="2" fill="transparent" stroke="{tstroke}" stroke-width="0.8"/>')
            out.append(text(x + 8 + tw / 2, y + 15, n["tag"], tfill, size=7, weight=400, family=MONO, extra=' letter-spacing="0.08em"'))
        out.append(text(cx, y + 32, n["name"], INK, weight=600))
        if n.get("sub"):
            out.append(text(cx, y + 47, n["sub"], MUTED, size=11))

    # 범례
    ly = lay.bot + 20
    out.append(f'<line x1="40" y1="{ly}" x2="{vw - 40}" y2="{ly}" stroke="rgba(45,49,66,0.10)" stroke-width="0.8"/>')
    out.append(text(40, ly + 28, "범례", MUTED, anchor="start"))
    items = [("box", "#ffffff", INK, "새로 만드는 업무 (태그 = 기능 모듈)")]
    if any(n.get("kind") == "now" for n in spec["nodes"]):
        items.append(("box", "rgba(45,49,66,0.03)", "rgba(45,49,66,0.30)", "지금 있는 화면"))
    legend = dict(LEGEND, **spec.get("legend", {}))
    for key in ("main", "back", "link", "focus"):
        if key in used or (key == "focus" and "focus-dash" in used):
            color, marker, dashed = STYLE[key]
            items.append(("dash" if dashed else "ln", color, marker, legend[key]))
    x = 112
    for kind, a, b, lb in items:
        if kind == "box":
            out.append(f'<rect x="{x}" y="{ly + 16}" width="28" height="16" rx="3" fill="{a}" stroke="{b}" stroke-width="1"/>')
        else:
            da = ' stroke-dasharray="4,3"' if kind == "dash" else ""
            out.append(f'<line x1="{x}" y1="{ly + 24}" x2="{x + 28}" y2="{ly + 24}" stroke="{a}" stroke-width="1.2"{da} marker-end="url(#{b})"/>')
        out.append(text(x + 40, ly + 28, lb, MUTED, anchor="start"))
        x += 40 + label_w(lb) + 28
    vh = ly + 48

    title = spec.get("title", "업무 흐름")
    desc = spec.get("desc", title)
    body = "\n      ".join(out)
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&family=Noto+Sans+KR:wght@400;500;600&family=Noto+Serif+KR:wght@400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --color-paper: #f5f5f5; --color-ink: #2d3142; --color-muted: #4f5d75; --color-accent: #bf4520;
      --font-sans: 'Geist', 'Noto Sans KR', 'Malgun Gothic', system-ui, sans-serif;
      --font-serif: 'Instrument Serif', 'Noto Serif KR', serif;
      --font-mono: 'Geist Mono', ui-monospace, monospace;
    }}
    body {{ font-family: var(--font-sans); background: var(--color-paper); color: var(--color-ink);
      min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 3rem 2rem; }}
    .frame {{ max-width: {vw}px; width: 100%; }}
    .eyebrow {{ font-family: var(--font-mono); font-size: 0.66rem; font-weight: 500; letter-spacing: 0.18em;
      text-transform: uppercase; color: var(--color-muted); margin-bottom: 0.5rem; }}
    h1 {{ font-family: var(--font-serif); font-size: clamp(1.5rem, 2.4vw + 0.75rem, 2rem); font-weight: 400;
      letter-spacing: -0.02em; line-height: 1.15; color: var(--color-ink); margin-bottom: 1.5rem; }}
    svg {{ width: 100%; min-width: 900px; display: block; }}
  </style>
</head>
<body>
  <div class="frame">
    <p class="eyebrow">{esc(spec.get("eyebrow", "Swimlane"))}</p>
    <h1>{esc(title)}</h1>

    <svg viewBox="0 0 {vw} {vh}" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="lane-title lane-desc">
      <title id="lane-title">{esc(title)}</title>
      <desc id="lane-desc">{esc(desc)}</desc>
      <defs>
        <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
        <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACC}"/></marker>
        <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
      </defs>

      <rect width="100%" height="100%" fill="{PAPER}"/>

      {body}
    </svg>
  </div>
</body>
</html>
''', vw, vh


def main(argv=None):
    ap = argparse.ArgumentParser(description="레인 그림 HTML 을 만든다")
    ap.add_argument("spec")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args(argv)
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    try:
        page, vw, vh = render(spec)
    except (KeyError, ValueError) as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 3
    Path(a.out).write_text(page, encoding="utf-8", newline="\n")
    print(f"OK: {a.out} ({vw}x{vh})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
