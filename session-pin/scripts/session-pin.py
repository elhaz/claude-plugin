#!/usr/bin/env python3
"""세션 핀 — 세션마다 미결 질문·진행 중·끝남을 볼트 노트 하나에 모은다.
Claude Code 의 pinboard(터미널 전용·세션 휘발)를 데스크톱 앱·Obsidian 환경에서 비슷하게 쓰려고 만들었다.

플러그인 훅에서 부른다 (hooks/hooks.json):
  UserPromptSubmit → session-pin.py prompt   ("핀" 이면 보드 전체, "핀 닫기" 면 노트 삭제, 아니면 미결 요약을 컨텍스트로 주입.
                                              방치된 다른 세션 노트도 함께 정리)
  Stop             → session-pin.py stop     (마지막 답변 끝의 질문을 맥락 한 토막과 함께 "미결 질문" 에 자동 추가)
  SessionEnd       → session-pin.py end      (열린 항목이 없으면 노트 삭제)

대화형 세션(Remote Control = CLAUDE_CODE_ENVIRONMENT_KIND=bridge, 터미널·데스크톱 앱·VS Code)에서만 동작한다.
배치 `claude -p` 에서는 아무것도 하지 않는다. SESSION_PIN=0/1 로 강제로 끄고 켤 수 있다.

노트 위치: $SESSION_PIN_DIR > $OBSIDIAN_VAULT/00_Inbox/세션 핀. 둘 다 없으면 아무것도 하지 않는다.

폰·데스크톱 앱은 세션을 직접 끝낼 수 없어 SessionEnd 가 거의 오지 않는다(아카이브 훅도 없음). 그래서
대화가 멈춘 세션의 노트를 정리한다 — 열린 항목이 없으면 1일, 있으면 3일 뒤. 대화가 멈췄는지는 세션 기록
파일(transcript)의 수정 시각으로 본다. 매핑(MAP_DIR)이 기기마다 따로라 각 기기는 자기 세션 노트만 지운다.
"""
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

_DIR = os.environ.get("SESSION_PIN_DIR") or (
    os.path.join(os.environ["OBSIDIAN_VAULT"], "00_Inbox", "세션 핀") if os.environ.get("OBSIDIAN_VAULT") else "")
PIN_DIR = Path(_DIR)
MAP_DIR = Path(os.environ.get("SESSION_PIN_MAP", Path.home() / ".claude" / "session-pins"))
SECTIONS = ("미결 질문", "진행 중", "끝남")
SHOW_RE = re.compile(r"^\s*/?핀(\s*(보여\s*줘|보기))?\s*[.!?]?\s*$")
CLOSE_RE = re.compile(r"^\s*/?핀\s*(닫기|닫아\s*줘|지워\s*줘|삭제)\s*[.!?]?\s*$")
STALE_DONE = 1 * 86400  # 열린 항목 없는 노트: 대화가 이만큼 멈추면 삭제
STALE_OPEN = 3 * 86400  # 열린 항목 남은 노트
CLAUDE_DIR = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


INTERACTIVE_ENTRYPOINTS = {"cli", "claude-desktop", "claude-vscode"}


def interactive() -> bool:
    force = os.environ.get("SESSION_PIN")
    if force in ("0", "1"):
        return force == "1"
    if os.environ.get("CLAUDE_CODE_ENVIRONMENT_KIND") == "bridge":
        return True
    return os.environ.get("CLAUDE_CODE_ENTRYPOINT") in INTERACTIVE_ENTRYPOINTS


def first_prompt(transcript: str) -> str:
    try:
        with open(transcript, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                if d.get("type") != "user" or d.get("isMeta"):
                    continue
                c = d.get("message", {}).get("content")
                if isinstance(c, list):
                    c = " ".join(b.get("text", "") for b in c if b.get("type") == "text")
                c = re.sub(r"<[^>]+>.*?</[^>]+>", " ", c or "", flags=re.S).strip()
                if c:
                    return c
    except (OSError, ValueError):
        pass
    return "세션"


def pin_path(sid: str, transcript: str, create: bool) -> Path | None:
    m = MAP_DIR / f"{sid}.path"
    if m.exists():
        p = Path(m.read_text(encoding="utf-8").splitlines()[0].strip())
        return p if p.exists() or create else None
    if not create:
        return None
    title = re.sub(r'[\\/:*?"<>|#^\[\]\n\r\t]+', " ", first_prompt(transcript))
    title = re.sub(r"\s+", " ", title).strip()[:24].strip() or "세션"
    p = PIN_DIR / f"{datetime.now():%Y-%m-%d %H%M} {title}.md"
    PIN_DIR.mkdir(parents=True, exist_ok=True)
    MAP_DIR.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f"---\nsession: {sid}\nstarted: {datetime.now():%Y-%m-%d %H:%M}\n---\n"
        f"# 세션 핀 — {title}\n\n" + "".join(f"## {s}\n\n" for s in SECTIONS),
        encoding="utf-8",
    )
    m.write_text(f"{p}\n{transcript}", encoding="utf-8")
    return p


def items(text: str, section: str) -> list[str]:
    m = re.search(rf"^## {section}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return [l for l in (m.group(1).splitlines() if m else []) if l.startswith("- [")]


def add_item(text: str, section: str, line: str) -> str:
    m = re.search(rf"^## {section}\n", text, re.M)
    if not m:
        return text.rstrip() + f"\n\n## {section}\n\n{line}\n"
    end = re.search(r"^## ", text[m.end():], re.M)
    cut = m.end() + (end.start() if end else len(text) - m.end())
    body = text[m.end():cut].rstrip("\n")
    return text[:m.end()] + (body + "\n" if body.strip() else "\n") + line + "\n\n" + text[cut:]


def last_reply(transcript: str) -> str:
    """마지막 사람 메시지 뒤에 나온 assistant 텍스트 중 맨 끝 것."""
    texts: list[str] = []
    try:
        with open(transcript, encoding="utf-8") as f:
            for line in f:
                d = json.loads(line)
                c = d.get("message", {}).get("content")
                if d.get("type") == "user" and not d.get("isMeta"):
                    if isinstance(c, str) or any(b.get("type") == "text" for b in c or []):
                        texts = []
                elif d.get("type") == "assistant" and isinstance(c, list):
                    t = "".join(b.get("text", "") for b in c if b.get("type") == "text")
                    if t.strip():
                        texts.append(t)
    except (OSError, ValueError):
        return ""
    return texts[-1] if texts else ""


def clean(line: str) -> str:
    line = re.sub(r"`([^`]*)`", lambda m: "" if "?" in m.group(1) else m.group(1), line)
    return re.sub(r"^\s*(?:[-*>#|]+|\d+[.)])\s*", "", line).replace("**", "").strip()


def questions(reply: str) -> list[tuple[str, str]]:
    """(질문, 맥락) 목록. 맥락 = 같은 줄의 질문 앞 문장, 짧으면 바로 앞 문단의 머리."""
    reply = re.sub(r"```.*?```", " ", reply, flags=re.S)
    lines = [clean(l) for l in reply[-1200:].splitlines()]
    out = []
    for i, line in enumerate(lines):
        for m in re.finditer(r"[^.!?\n]*\?", line):
            q = m.group(0).strip(" -—:")
            if not 6 <= len(q) <= 160:
                continue
            ctx = line[:m.start()].strip()
            if len(ctx) < 15:
                j = i - 1
                while j >= 0 and not lines[j]:
                    j -= 1
                para = []
                while j >= 0 and lines[j]:
                    para.insert(0, lines[j])
                    j -= 1
                ctx = " ".join(para)
            ctx = re.sub(r"\s+", " ", ctx).strip()
            out.append((q, ctx[:140] + ("…" if len(ctx) > 140 else "")))
    return out


def norm(s: str) -> str:
    s = re.sub(r"^- \[.\]\s*", "", s)
    s = re.sub(r"\s*\(\d\d:\d\d\).*$", "", s)  # 시각·맥락 꼬리는 비교에서 뺀다
    return re.sub(r"[\s?.,·]+", "", s)


def cmd_stop(ev: dict) -> None:
    qs = questions(last_reply(ev.get("transcript_path", "")))
    if not qs:
        return
    p = pin_path(ev["session_id"], ev.get("transcript_path", ""), create=True)
    text = p.read_text(encoding="utf-8")
    seen = {norm(l) for s in SECTIONS for l in items(text, s)}
    stamp = datetime.now().strftime("%H:%M")
    for q, ctx in qs:
        if norm(q) not in seen:
            text = add_item(text, "미결 질문", f"- [ ] {q} ({stamp})" + (f" — {ctx}" if ctx else ""))
            seen.add(norm(q))
    p.write_text(text, encoding="utf-8")


def has_open(text: str) -> bool:
    return any(l.startswith("- [ ]") for s in SECTIONS for l in items(text, s))


def drop(sid: str, p: Path | None) -> None:
    if p is not None:
        p.unlink(missing_ok=True)
    (MAP_DIR / f"{sid}.path").unlink(missing_ok=True)


def last_active(m: Path) -> float:
    """세션 기록 파일의 수정 시각. 못 찾으면 매핑 파일 시각."""
    lines = m.read_text(encoding="utf-8").splitlines()
    cands = [Path(lines[1].strip())] if len(lines) > 1 and lines[1].strip() else []
    cands += list((CLAUDE_DIR / "projects").glob(f"*/{m.stem}.jsonl"))
    times = [c.stat().st_mtime for c in cands if c.exists()]
    return max(times) if times else m.stat().st_mtime


def sweep(current: str) -> None:
    """대화가 멈춘 다른 세션의 노트를 지운다."""
    if not MAP_DIR.is_dir():
        return
    now = time.time()
    for m in MAP_DIR.glob("*.path"):
        if m.stem == current:
            continue
        try:
            p = Path(m.read_text(encoding="utf-8").splitlines()[0].strip())
            if not p.exists():
                drop(m.stem, None)
                continue
            limit = STALE_OPEN if has_open(p.read_text(encoding="utf-8")) else STALE_DONE
            if now - last_active(m) > limit:
                drop(m.stem, p)
        except (OSError, IndexError):
            continue


def cmd_prompt(ev: dict) -> None:
    sid, tr = ev["session_id"], ev.get("transcript_path", "")
    sweep(sid)
    if CLOSE_RE.match(ev.get("prompt", "")):
        p = pin_path(sid, tr, create=False)
        drop(sid, p)
        ctx = (f"[세션 핀] 사용자 요청으로 이 세션 핀 노트를 지웠다({p.name if p else '노트 없음'}). "
               f"지웠다고 한 줄로만 알린다. 이후 답변 끝에 질문이 나오면 노트가 새로 생긴다.")
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}}))
        return
    show = bool(SHOW_RE.match(ev.get("prompt", "")))
    p = pin_path(sid, tr, create=show)
    if p is None:
        ctx = (f"[세션 핀] 이 세션의 핀 노트는 아직 없다. 여러 단계 작업을 시작하면 "
               f"`{PIN_DIR}/` 에 이 세션 노트가 생긴다(`핀` 이라고 치면 생성).")
        if not show:
            ctx = ""
    else:
        text = p.read_text(encoding="utf-8")
        if show:
            board = text.split("---", 2)[-1].strip()
            ctx = (f"[세션 핀] 사용자가 보드를 요청했다. 아래 보드를 그대로 보여 주고, 보드가 실제와 어긋나 있으면 "
                   f"파일(`{p}`)부터 고친 뒤 보여 준다. 해설은 붙이지 않는다.\n\n{board}")
        else:
            opened = [l for l in items(text, "미결 질문") + items(text, "진행 중") if l.startswith("- [ ]")]
            ctx = (f"[세션 핀] `{p}` — 이번 메시지로 답이 된 미결 질문은 [x] 로 바꿔 「끝남」 으로 옮기고, "
                   f"여러 단계 작업은 「진행 중」 에 한 줄로 두었다가 끝나면 「끝남」 으로 옮긴다(작업 단위, 사소한 도구 호출은 제외).")
            if opened:
                ctx += "\n열린 항목:\n" + "\n".join(opened[:12])
    if ctx:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                 "additionalContext": ctx}}))  # ASCII 이스케이프 — Windows 콘솔 인코딩 회피


def cmd_end(ev: dict) -> None:
    p = pin_path(ev["session_id"], "", create=False)
    if p is None:
        return
    if not has_open(p.read_text(encoding="utf-8")):
        drop(ev["session_id"], p)


def main() -> None:
    if len(sys.argv) < 2 or not interactive() or not _DIR:
        return
    try:
        ev = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except ValueError:
        return
    if not ev.get("session_id"):
        return
    {"stop": cmd_stop, "prompt": cmd_prompt, "end": cmd_end}.get(sys.argv[1], lambda e: None)(ev)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 훅 실패가 대화를 막지 않게
        print(f"session-pin: {e}", file=sys.stderr)
