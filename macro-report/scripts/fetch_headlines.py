#!/usr/bin/env python3
"""거시경제 주간 보고 v2 — 한 주치 뉴스 헤드라인을 뉴스·전망 scanner 입력 파일로.

데이터 플랫폼이 3시간마다 누적한 RSS 헤드라인(`/api/news/headlines`, 내부망 전용)을
받아, 거시 관련 키워드로 거른 뒤 마크다운 표로 쓴다. scanner 는 WebFetch 만 쓰는데
WebFetch 로는 연합뉴스에 접속할 수 없고 내부망 API 도 부를 수 없어서, 오케스트레이터가
Bash 로 이 스크립트를 먼저 돌린다.

연합뉴스 RSS 는 비상업적 개인 용도만 허용된다 — 이 파일은 공개 게시하지 않는다.

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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", required=True, help="이 날짜(UTC) 이후 발행분 — 보통 지난 판단일")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--api-base", default=os.getenv("FDP_INTERNAL_BASE", "http://localhost:8000"),
                    help="내부망 주소여야 한다 (공개 주소는 403)")
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
        "> fetch_headlines.py 생성. 내부 입력 전용 — 공개 게시 금지 (연합뉴스 RSS 는 개인 용도만 허용).",
        f"> 전체 {len(rows)}건 중 거시 관련 {len(kept)}건: "
        + ", ".join(f"{k} {v}" for k, v in sorted(by_source.items())), "",
        "| 시각(UTC) | 출처 | 제목 | 링크 |", "|---|---|---|---|",
    ]
    for published, source, _feed, title, link in kept:
        title = title.replace("|", "／")
        lines.append(f"| {published} | {source} | {title} | {link} |")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"저장 완료: {args.out} ({len(kept)}/{len(rows)}건)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
