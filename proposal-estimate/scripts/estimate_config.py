"""설정 읽기 — 플러그인 기본값(config/settings.json) 위에 사용자 덮어쓰기 파일을 얹는다.

덮어쓰기 파일 위치 (앞에 있는 것이 먼저):
1. 환경변수 PROPOSAL_ESTIMATE_CONFIG 가 가리키는 파일
2. ~/.claude/proposal-estimate.json
"""

import json
import math
import os
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = PLUGIN_ROOT / "config" / "settings.json"


def _merge(base, over):
    # 딕셔너리는 키 단위로 겹치고, 나머지 값은 덮어쓴다
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def user_config_path():
    env = os.environ.get("PROPOSAL_ESTIMATE_CONFIG")
    if env:
        return Path(env)
    return Path.home() / ".claude" / "proposal-estimate.json"


def load(path=None):
    cfg = json.loads(DEFAULT_PATH.read_text(encoding="utf-8"))
    over = Path(path) if path else user_config_path()
    if over.is_file():
        cfg = _merge(cfg, json.loads(over.read_text(encoding="utf-8")))
    return cfg


def round_md(x, unit=0.5):
    # 0.5 단위 반올림(사사오입). 파이썬 round 의 짝수 반올림을 쓰지 않는다
    return math.floor(x / unit + 0.5) * unit


def tilde(s):
    # 볼트 마크다운에서 ~ 두 개가 취소선이 되지 않게 표 안 범위 표기는 \~ 로 쓴다
    return str(s).replace("\\~", "~").replace("~", "\\~")