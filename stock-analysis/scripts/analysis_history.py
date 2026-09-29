#!/usr/bin/env python3
"""종목분석 문서의 날짜별 이력 — 최신본은 제자리에 두고 이전 판을 `이력/{문서명}/{날짜}.md` 로 보관한다.

    archive <문서>   덮어쓰기 전에 호출. 문서의 updated 날짜로 이력 사본을 만든다.
                     이력본은 태그 `종목분석` → `종목분석이력` 으로 바꿔 대시보드(태그 필터)에 겹쳐 뜨지 않게 한다.
    link <문서>      쓰기가 끝난 뒤 호출. 최신본 끝의 `## 이전 분석` 절을 이력 폴더 기준으로 다시 쓴다.

사용:
    python3 analysis_history.py archive "$V/03_Resources/주식분석/종목분석/알파벳.md"
    python3 analysis_history.py link    "$V/03_Resources/주식분석/종목분석/알파벳.md"
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

HISTORY_DIR = "이력"
SECTION = "## 이전 분석"
TAG, HISTORY_TAG = "종목분석", "종목분석이력"
_DATE = re.compile(r"^(?:updated|마지막수정일):\s*['\"]?(\d{4}-\d{2}-\d{2})", re.M)
_WORD = r"[\w가-힣/]"


def doc_date(text: str, path: Path) -> str:
    m = _DATE.search(split_front(text)[0])
    return m.group(1) if m else date.fromtimestamp(path.stat().st_mtime).isoformat()


def split_front(text: str) -> tuple[str, str]:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[:end + 4], text[end + 4:]
    return "", text


def retag(text: str, stem: str) -> str:
    """이력본: 태그를 바꾸고 최신본 링크를 단다. 본문 해시태그도 Dataview 태그로 잡히므로 같이 바꾼다."""
    front, body = split_front(text)
    front = re.sub(rf"(^\s*-\s*|[\[,]\s*){TAG}(?!{_WORD})", rf"\g<1>{HISTORY_TAG}", front, flags=re.M)
    body = re.sub(rf"#{TAG}(?!{_WORD})", f"#{HISTORY_TAG}", body)
    body = strip_section(body)
    note = f"\n> [!info] 이력본 — 최신 분석은 [[{stem}]]\n"
    return front + note + body


def strip_section(body: str) -> str:
    i = body.find(f"\n{SECTION}\n")
    if i == -1:
        return body
    j = body.find("\n## ", i + 1)
    return body[:i] + (body[j:] if j != -1 else "\n")


def archive(doc: Path) -> Path | None:
    if not doc.exists():
        return None
    text = doc.read_text(encoding="utf-8")
    d = doc_date(text, doc)
    folder = doc.parent / HISTORY_DIR / doc.stem
    folder.mkdir(parents=True, exist_ok=True)
    out, n = folder / f"{d}.md", 2
    while out.exists():
        if out.read_text(encoding="utf-8") == retag(text, doc.stem):
            return out                       # 같은 판을 이미 보관함
        out, n = folder / f"{d}-{n}.md", n + 1
    out.write_text(retag(text, doc.stem), encoding="utf-8")
    return out


def link(doc: Path) -> int:
    folder = doc.parent / HISTORY_DIR / doc.stem
    files = sorted(folder.glob("*.md"), reverse=True) if folder.is_dir() else []
    text = doc.read_text(encoding="utf-8")
    front, body = split_front(text)
    body = strip_section(body).rstrip("\n")
    if files:
        items = "\n".join(f"- [[{HISTORY_DIR}/{doc.stem}/{f.stem}|{f.stem}]]" for f in files)
        body += f"\n\n{SECTION}\n\n{items}\n"
    else:
        body += "\n"
    doc.write_text(front + body, encoding="utf-8")
    return len(files)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["archive", "link"])
    ap.add_argument("docs", nargs="+", type=Path)
    args = ap.parse_args(argv)
    for doc in args.docs:
        if args.action == "archive":
            out = archive(doc)
            print(f"archive: {doc.name} → {out if out else '기존 문서 없음(신규)'}")
        else:
            print(f"link: {doc.name} 이력 {link(doc)}개")
    return 0


if __name__ == "__main__":
    sys.exit(main())
