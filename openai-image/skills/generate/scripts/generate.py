#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai>=1.60",
# ]
# ///
"""
OpenAI 이미지 생성/편집 스크립트.

기본 사용:
    uv run generate.py --prompt "미니멀 기하학 로고" --output ./logo.png
    uv run generate.py --prompt "히어로 이미지" --output ./hero.png --model hq --size 1536x1024
    uv run generate.py --prompt "투명 배경 아이콘" --output ./icon.png --background transparent
    uv run generate.py --prompt "스케치 스타일" --output ./edit.png --edit ./photo.png

프롬프트 확장이 필요하면 호출 측(Claude)에서 prompt-rewriter 에이전트를 먼저 실행하고
반환된 확장 프롬프트를 --prompt로 넘긴다. 이 스크립트 자체는 LLM 호출을 하지 않는다.

환경변수:
    OPENAI_API_KEY  (필수)
"""

import argparse
import base64
import os
import sys
import time
from pathlib import Path

from openai import OpenAI

MODEL_ALIASES = {
    "fast": "gpt-image-1-mini",
    "hq": "gpt-image-1.5",   # 조직 인증 불필요. 일반 용도 기본 고품질
    "v2": "gpt-image-2",     # 조직 인증(신분증 촬영) 완료된 계정에서만 호출 가능
    # 스냅샷 고정이 필요하면 원시 ID 직접 지정:
    #   gpt-image-1 / gpt-image-2-2026-04-21
}

SIZE_CHOICES = ["1024x1024", "1536x1024", "1024x1536", "auto"]
QUALITY_CHOICES = ["low", "medium", "high", "auto"]
BACKGROUND_CHOICES = ["auto", "transparent", "opaque"]
FORMAT_CHOICES = ["png", "jpeg", "webp"]


def log(msg: str) -> None:
    # stderr로 진행 로그를 흘려 사용자가 대기 중 상태를 확인할 수 있도록 한다
    print(f"[openai-image] {msg}", file=sys.stderr, flush=True)


def resolve_model(value: str) -> str:
    return MODEL_ALIASES.get(value, value)


def save_b64_images(images_b64: list[str], output_path: str) -> list[str]:
    # 여러 장일 경우 -1, -2 접미사를 붙여 저장
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    saved = []
    for idx, b64 in enumerate(images_b64):
        if len(images_b64) == 1:
            target = out
        else:
            target = out.with_name(f"{out.stem}-{idx + 1}{out.suffix}")
        target.write_bytes(base64.b64decode(b64))
        saved.append(str(target))
    return saved


def run_generate(client: OpenAI, args: argparse.Namespace, prompt: str) -> list[str]:
    params = {
        "model": resolve_model(args.model),
        "prompt": prompt,
        "size": args.size,
        "quality": args.quality,
        "background": args.background,
        "output_format": args.format,
        "n": args.n,
    }
    log(f"generate 요청: model={params['model']} size={args.size} quality={args.quality}")
    t0 = time.monotonic()
    if args.stream:
        return _stream_generate(client, params)
    resp = client.images.generate(**params, timeout=args.timeout)
    log(f"응답 수신 ({time.monotonic() - t0:.1f}s 소요)")
    return [item.b64_json for item in resp.data]


def run_edit(client: OpenAI, args: argparse.Namespace, prompt: str) -> list[str]:
    edit_path = Path(args.edit)
    if not edit_path.exists():
        log(f"편집 대상 이미지 없음: {edit_path}")
        sys.exit(1)
    params = {
        "model": resolve_model(args.model),
        "prompt": prompt,
        "image": edit_path.open("rb"),
        "size": args.size,
        "quality": args.quality,
        "background": args.background,
        "output_format": args.format,
        "n": args.n,
    }
    if args.mask:
        mask_path = Path(args.mask)
        if not mask_path.exists():
            log(f"마스크 이미지 없음: {mask_path}")
            sys.exit(1)
        params["mask"] = mask_path.open("rb")
    log(f"edit 요청: model={params['model']} size={args.size} quality={args.quality}")
    t0 = time.monotonic()
    resp = client.images.edit(**params, timeout=args.timeout)
    log(f"응답 수신 ({time.monotonic() - t0:.1f}s 소요)")
    return [item.b64_json for item in resp.data]


def _stream_generate(client: OpenAI, params: dict) -> list[str]:
    # stream=True + partial_images=2로 진행 상황을 실시간 알림
    params = {**params, "stream": True, "partial_images": 2}
    t0 = time.monotonic()
    final_b64: list[str] = []
    for event in client.images.generate(**params):
        event_type = getattr(event, "type", "")
        if "partial_image" in event_type:
            idx = getattr(event, "partial_image_index", "?")
            log(f"중간 이미지 수신 #{idx} ({time.monotonic() - t0:.1f}s)")
        elif "completed" in event_type:
            b64 = getattr(event, "b64_json", None)
            if b64:
                final_b64.append(b64)
            log(f"생성 완료 ({time.monotonic() - t0:.1f}s)")
    if not final_b64:
        log("스트림에서 최종 이미지가 오지 않음")
        sys.exit(1)
    return final_b64


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAI 이미지 생성/편집")
    parser.add_argument("--prompt", required=True, help="이미지 설명 또는 편집 지시")
    parser.add_argument("--output", required=True, help="출력 파일 경로")
    parser.add_argument(
        "--model",
        default="fast",
        help="fast|hq 별칭 또는 원시 모델 ID (기본: fast=gpt-image-1-mini)",
    )
    parser.add_argument("--size", choices=SIZE_CHOICES, default="1024x1024")
    parser.add_argument("--quality", choices=QUALITY_CHOICES, default="medium")
    parser.add_argument("--background", choices=BACKGROUND_CHOICES, default="auto")
    parser.add_argument("--format", choices=FORMAT_CHOICES, default="webp")
    parser.add_argument("--n", type=int, default=1, help="생성 개수 (1~4)")
    parser.add_argument("--edit", help="편집 모드: 원본 이미지 경로")
    parser.add_argument("--mask", help="편집 시 마스크 PNG (투명 영역 = 편집 대상)")
    parser.add_argument("--timeout", type=float, default=120.0, help="초 단위 타임아웃")
    parser.add_argument(
        "--stream",
        action="store_true",
        help="스트리밍 모드 (중간 진행 로그 + partial_images)",
    )
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        log("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    if args.n < 1 or args.n > 4:
        log("n은 1~4 범위여야 합니다.")
        sys.exit(1)

    client = OpenAI()

    try:
        if args.edit:
            images_b64 = run_edit(client, args, args.prompt)
        else:
            images_b64 = run_generate(client, args, args.prompt)
    except Exception as exc:
        log(f"API 호출 실패: {type(exc).__name__}: {exc}")
        sys.exit(1)

    saved = save_b64_images(images_b64, args.output)
    for p in saved:
        print(p)
    log(f"{len(saved)}개 파일 저장 완료")


if __name__ == "__main__":
    main()
