#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
#     "pillow",
# ]
# ///
"""
Multi-turn 대화형 이미지 편집 using Google's Gemini image models.

채팅 세션을 통해 이미지를 반복적으로 편집할 수 있습니다.
이전 편집 컨텍스트가 유지되어 연속적인 수정이 가능합니다.

Usage:
    # 대화형 모드 (터미널에서 직접 입력)
    uv run chat.py --image "./photo.png" --output-dir "./edits"

    # 단일 턴 모드 (하나의 편집 지시)
    uv run chat.py --image "./photo.png" --output "./edited.png" --prompt "배경을 흐리게 해줘"

    # 다중 턴 모드 (여러 편집 지시를 순차 적용)
    uv run chat.py --image "./photo.png" --output "./final.png" \
        --prompt "만화 스타일로 변환" \
        --prompt "배경을 파란색으로" \
        --prompt "밝기를 높여줘"

    # 이전 세션 이어서 편집 (세션 파일 사용)
    uv run chat.py --session "./session.json" --output "./continued.png" --prompt "색상을 더 선명하게"
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

MODEL_IDS = {
    "flash": "gemini-2.5-flash-image",
    "pro": "gemini-3-pro-image-preview",
}


def save_session(session_file: str, history: list, last_image_path: str) -> None:
    """세션 정보를 JSON 파일로 저장"""
    session_data = {
        "history": history,
        "last_image": last_image_path,
        "updated_at": datetime.now().isoformat(),
    }
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
    print(f"Session saved to: {session_file}")


def load_session(session_file: str) -> tuple[list, str]:
    """세션 파일에서 히스토리와 마지막 이미지 경로 로드"""
    with open(session_file, "r", encoding="utf-8") as f:
        session_data = json.load(f)
    return session_data.get("history", []), session_data.get("last_image", "")


def run_chat_session(
    image_path: str | None,
    prompts: list[str],
    output_path: str | None,
    output_dir: str | None,
    session_file: str | None,
    model: str = "flash",
    interactive: bool = False,
) -> None:
    """Multi-turn 이미지 편집 세션 실행"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    model_id = MODEL_IDS[model]

    # 세션 로드 또는 새 세션 시작
    history = []
    current_image_path = image_path

    if session_file and os.path.exists(session_file):
        history, current_image_path = load_session(session_file)
        print(f"Session loaded from: {session_file}")
        print(f"Previous edits: {len(history)}")

    if not current_image_path or not os.path.exists(current_image_path):
        print("Error: No valid image to edit", file=sys.stderr)
        sys.exit(1)

    # 출력 디렉토리 설정
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 채팅 세션 생성
    chat = client.chats.create(
        model=model_id,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    # 초기 이미지 로드
    current_image = Image.open(current_image_path)
    turn_count = len(history)

    def process_prompt(prompt: str) -> str | None:
        """단일 프롬프트 처리 및 결과 이미지 저장"""
        nonlocal current_image, turn_count

        # 첫 번째 턴이면 이미지와 함께 전송
        if turn_count == 0:
            response = chat.send_message([current_image, f"Edit this image: {prompt}"])
        else:
            response = chat.send_message(f"Edit the image: {prompt}")

        # 응답에서 이미지 추출
        result_image = None
        response_text = None

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                response_text = part.text
                print(f"Model: {response_text}")
            elif part.inline_data is not None:
                result_image = part.as_image()

        if result_image is None:
            print(f"Warning: No image generated for prompt: {prompt}", file=sys.stderr)
            return None

        turn_count += 1
        history.append({"turn": turn_count, "prompt": prompt, "response": response_text})

        # 이미지 저장
        if output_dir:
            save_path = os.path.join(output_dir, f"edit_{turn_count:03d}.png")
        elif output_path and not interactive:
            save_path = output_path
        else:
            save_path = f"edit_{turn_count:03d}.png"

        result_image.save(save_path)
        print(f"[Turn {turn_count}] Image saved to: {save_path}")

        current_image = result_image
        return save_path

    # 프롬프트 처리
    last_saved_path = current_image_path

    if prompts:
        # 비대화형 모드: 주어진 프롬프트들 순차 처리
        for prompt in prompts:
            print(f"\n[Turn {turn_count + 1}] Processing: {prompt}")
            saved_path = process_prompt(prompt)
            if saved_path:
                last_saved_path = saved_path

    if interactive:
        # 대화형 모드
        print("\n=== Multi-turn Image Editing Session ===")
        print("Type your edit instructions. Commands:")
        print("  'save' - Save current session")
        print("  'quit' or 'exit' - End session")
        print("  'history' - Show edit history")
        print("=" * 40)

        while True:
            try:
                user_input = input(f"\n[Turn {turn_count + 1}] Edit> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nSession ended.")
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("Session ended.")
                break

            if user_input.lower() == "save":
                if session_file:
                    save_session(session_file, history, last_saved_path)
                else:
                    default_session = "chat_session.json"
                    save_session(default_session, history, last_saved_path)
                continue

            if user_input.lower() == "history":
                print("\n=== Edit History ===")
                for h in history:
                    print(f"  Turn {h['turn']}: {h['prompt']}")
                continue

            saved_path = process_prompt(user_input)
            if saved_path:
                last_saved_path = saved_path

    # 최종 세션 저장
    if session_file:
        save_session(session_file, history, last_saved_path)

    print(f"\nTotal edits: {turn_count}")
    print(f"Final image: {last_saved_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Multi-turn image editing with Gemini chat"
    )
    parser.add_argument(
        "--image",
        help="Initial image to edit",
    )
    parser.add_argument(
        "--prompt",
        action="append",
        dest="prompts",
        metavar="TEXT",
        help="Edit instruction (can be used multiple times for multi-turn)",
    )
    parser.add_argument(
        "--output",
        help="Output file path for final image (single output mode)",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for all intermediate images",
    )
    parser.add_argument(
        "--session",
        help="Session file to save/load conversation history",
    )
    parser.add_argument(
        "--model",
        choices=["flash", "pro"],
        default="flash",
        help="Model: flash (fast) or pro (high-quality) (default: flash)",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode (terminal input)",
    )

    args = parser.parse_args()

    # 검증: 이미지 또는 세션 필요
    if not args.image and not (args.session and os.path.exists(args.session)):
        parser.error("Either --image or existing --session file is required")

    # 검증: 프롬프트 또는 대화형 모드 필요
    if not args.prompts and not args.interactive:
        parser.error("Either --prompt or --interactive mode is required")

    run_chat_session(
        image_path=args.image,
        prompts=args.prompts or [],
        output_path=args.output,
        output_dir=args.output_dir,
        session_file=args.session,
        model=args.model,
        interactive=args.interactive,
    )


if __name__ == "__main__":
    main()
