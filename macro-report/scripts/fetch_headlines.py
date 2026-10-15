#!/usr/bin/env python3
"""거시경제 주간 보고 v2 — 한 주치 뉴스 헤드라인을 뉴스·전망 scanner 입력 파일로.

데이터 플랫폼이 3시간마다 누적한 RSS 헤드라인(`/api/news/headlines`, 내부망 전용)을
받아, 거시 관련 키워드로 거른 뒤 마크다운 표로 쓴다. scanner 는 WebFetch 만 쓰는데
WebFetch 로는 연합뉴스에 접속할 수 없고 내부망 API 도 부를 수 없어서, 오케스트레이터가
Bash 로 이 스크립트를 먼저 돌린다.

데이터 플랫폼이 SAVE 앱 기사도 모으면(`/api/news/articles`·`/api/news/reports`, fdp v0.26+)
같은 파일에 더한다 — SAVE PICK(편집자가 고른 기사)은 전부, 로이터 AI 번역은 거시 키워드로
거르고, SAVE 리포트는 날짜별 "오늘의 소식" 기사 제목만. 없으면(옛 fdp) 건너뛴다.

연합뉴스 RSS·SAVE 기사는 개인 용도 자료다 — 이 파일은 공개 게시하지 않는다.

사용:
    fetch_headlines.py --since YYYY-MM-DD --out <데이터/날짜/뉴스헤드라인.md>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# 연합뉴스 경제는 하루 약 300건이라 거시 관련만 남긴다. CNBC·연준은 양이 적어 전부 둔다.
KEYWORDS = [
    "금리", "연준", "Fed", "FOMC", "파월", "물가", "CPI", "PCE", "인플레", "고용", "실업",
    "환율", "원/달러", "원·달러", "달러", "국채", "채권", "관세", "무역", "수출", "수입",
    "유가", "원유", "OPEC", "반도체", "AI", "엔비디아", "중국", "일본", "유럽", "ECB", "BOJ",
    "한은", "한국은행", "기준금리", "성장률", "GDP", "경기", "침체", "재정", "부채", "예산",
    "전쟁", "분쟁", "제재", "이란", "러시아", "우크라이나", "이스라엘", "호르무즈", "홍해",
    "트럼프", "백악관", "의회", "셧다운", "코스피", "증시", "나스닥", "S&P", "다우", "금값",
    "금 가격", "비트코인", "신용", "은행", "부도", "사모", "IMF", "OECD", "외환",
]
FULL_SOURCES = {"CNBC", "Fed"}


def fetch(base: str, since: str) -> list[list]:
    qs = urllib.parse.urlencode({"since": since, "limit": 5000})
    req = urllib.request.Request(
        f"{base}/api/news/headlines?{qs}",
        headers={"User-Agent": "macro-report-headlines/2.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]


def relevant(source: str, title: str) -> bool:
    return source in FULL_SOURCES or any(k.lower() in title.lower() for k in KEYWORDS)


def get_json(base: str, path: str, **query):
    qs = urllib.parse.urlencode(query)
    req = urllib.request.Request(
        f"{base}{path}" + (f"?{qs}" if qs else ""),
        headers={"User-Agent": "macro-report-headlines/2.2", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def save_articles(base: str, since: str) -> list[dict]:
    """SAVE 기사 목록 (본문 제외). 플랫폼에 없으면 빈 목록."""
    try:
        body = get_json(base, "/api/news/articles", since=since, body="false", limit=2000)
    except Exception:  # noqa: BLE001 — 옛 fdp 거나 SAVE 수집이 없음
        return []
    return [dict(zip(body["columns"], r, strict=False)) for r in body["data"]]


def save_report_titles(base: str, since: str) -> list[tuple[str, list[str]]]:
    """기간 안 SAVE 리포트의 (날짜, "오늘의 소식" 기사 제목들). 없으면 빈 목록."""
    try:
        rows = get_json(base, "/api/news/reports", limit=60)["data"]
    except Exception:  # noqa: BLE001
        return []
    out = []
    for report_date, *_ in rows:
        if report_date < since:
            continue
        try:
            text = get_json(base, f"/api/news/reports/{report_date}").get("text") or ""
        except Exception:  # noqa: BLE001
            continue
        titles = [ln[4:].strip() for ln in text.splitlines() if ln.startswith("### ")]
        out.append((report_date, titles))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", required=True, help="이 날짜(UTC) 이후 발행분 — 보통 지난 판단일")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--api-base", default=os.getenv("FDP_API_BASE") or "http://localhost:8000",
                    help="기본 FDP_API_BASE → localhost. 내부망 주소여야 한다 (공개 주소는 403)")
    args = ap.parse_args()

    try:
        rows = fetch(args.api_base, args.since)
    except Exception as e:  # noqa: BLE001
        print(f"헤드라인 조회 실패 ({args.api_base}): {e}", file=sys.stderr)
        return 1

    kept = [r for r in rows if relevant(r[1], r[3])]
    by_source: dict[str, int] = {}
    for r in kept:
        by_source[r[1]] = by_source.get(r[1], 0) + 1

    lines = [
        f"# 뉴스 헤드라인 ({args.since} 이후)", "",
        "> fetch_headlines.py 생성. 내부 입력 전용 — 공개 게시 금지 (연합뉴스 RSS·SAVE 기사는 개인 용도만).",
        f"> 전체 {len(rows)}건 중 거시 관련 {len(kept)}건: "
        + ", ".join(f"{k} {v}" for k, v in sorted(by_source.items())), "",
        "| 시각(UTC) | 출처 | 제목 | 링크 |", "|---|---|---|---|",
    ]
    for published, source, _feed, title, link in kept:
        title = title.replace("|", "／")
        lines.append(f"| {published} | {source} | {title} | {link} |")
    arts = save_articles(args.api_base, args.since)
    picks = [a for a in arts if a["source"] == "SAVE PICK"]
    reuters = [a for a in arts if a["source"] != "SAVE PICK" and relevant(a["source"], a["title"])]
    if arts:
        lines += [
            "", f"## SAVE 기사 — SAVE PICK {len(picks)}건 전부 · 로이터 번역 {len(reuters)}건(거시 관련만, 전체 "
            f"{len(arts) - len(picks)}건)", "",
            "> SAVE 앱(세이브티커) 기사를 데이터 플랫폼이 수집한 것. 기사 주소가 없어 링크 대신 관련 티커를 둔다.",
            "> SAVE PICK 은 편집자가 중요하다고 고른 기사다.", "",
            "| 시각(UTC) | 출처 | 분류 | 제목 | 티커 |", "|---|---|---|---|---|",
        ]
        for a in sorted(picks + reuters, key=lambda a: a["published_at"]):
            title = a["title"].replace("|", "／")
            lines.append(f"| {a['published_at'][:16]} | {a['source']} | {a.get('category') or ''} | "
                         f"{title} | {a.get('tickers') or ''} |")
    reports = save_report_titles(args.api_base, args.since)
    if reports:
        lines += ["", f"## SAVE 리포트 — 날짜별 \"오늘의 소식\" 제목 ({len(reports)}부)", ""]
        for report_date, titles in reports:
            lines.append(f"- **{report_date}**: " + (" · ".join(titles) if titles else "(제목 없음)"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"저장 완료: {args.out} (RSS {len(kept)}/{len(rows)}건 · SAVE {len(picks) + len(reuters)}/{len(arts)}건"
          f" · 리포트 {len(reports)}부)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
