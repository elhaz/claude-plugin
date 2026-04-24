---
name: openai-image
description: OpenAI gpt-image 모델로 이미지를 생성·편집한다
argument-hint: <prompt> [--output path] [--model fast|hq] [--size WxH] [--edit path] [--mask path] [--rewrite]
allowed-tools:
  - Bash
  - Read
  - Write
  - Agent
---

# /openai-image - OpenAI 이미지 생성 커맨드

`gpt-image-2`(플래그십) / `gpt-image-1-mini`(고속)를 사용해 이미지를 생성하거나 편집한다. `gpt-image-1`, `gpt-image-1.5`, `gpt-image-2-2026-04-21` 스냅샷도 `--model`에 원시 ID로 지정 가능.

## 사용 방법

```
/openai-image "이미지 설명"
/openai-image "설명" --output ./path/to/image.png
/openai-image "설명" --model hq --size 1536x1024 --quality high
/openai-image "투명 배경 로고" --background transparent
/openai-image "배경을 석양으로" --edit ./original.png --mask ./mask.png
/openai-image "cat" --rewrite
```

## 옵션

| 옵션 | 값 | 기본값 |
|------|-----|--------|
| `--output` | PNG/JPEG/WebP 경로 (확장자는 `--format`과 맞추는 것이 이상적) | `./generated-image.webp` |
| `--model` | `fast`(mini) / `hq`(gpt-image-2) / 원시 ID | `fast` |
| `--size` | `1024x1024` / `1536x1024` / `1024x1536` / `auto` | `1024x1024` |
| `--quality` | `low` / `medium` / `high` / `auto` | `medium` |
| `--background` | `auto` / `transparent` / `opaque` | `auto` |
| `--format` | `png` / `jpeg` / `webp` | `webp` |
| `--n` | 1~4 | 1 |
| `--edit` | 편집 대상 원본 이미지 | - |
| `--mask` | 편집 마스크 PNG (투명 영역이 대상) | - |
| `--rewrite` | prompt-rewriter 서브에이전트로 프롬프트 확장 (커맨드 레벨 힌트, CLI 플래그 아님) | off |
| `--timeout` | 초 | 120 |
| `--stream` | 스트리밍 진행 로그 | off |

## 실행 방법

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/generate/scripts/generate.py" \
  --prompt "프롬프트" \
  --output "출력경로.png" \
  [옵션들]
```

## 워크플로우

1. 사용자 인자에서 프롬프트와 옵션 파싱
2. `--output` 미지정 시 현재 디렉토리의 `generated-image.webp`로 저장 (포맷을 바꾸면 확장자도 맞춰서 지정)
3. **`--rewrite` 지정 또는 원본 프롬프트가 단순(예: 3단어 이하)한 경우**: Agent 도구로 `subagent_type: prompt-rewriter`를 호출해 상세 영문 프롬프트를 받는다. 에이전트 반환값을 실제 `--prompt` 값으로 사용
4. `generate.py` 실행. stderr 진행 로그로 API 상태 확인
5. 완료 후 저장된 파일 경로 안내

### prompt-rewriter 호출 방법

Claude는 Agent 도구를 다음과 같이 호출한다:

```
Agent(
  description="이미지 프롬프트 확장",
  subagent_type="prompt-rewriter",
  prompt="원본 프롬프트: <사용자 프롬프트>\n용도 힌트: <hero/logo/icon 등 추정>\n스타일 힌트: <있다면>"
)
```

에이전트는 확장된 영문 단락만 반환한다. 해당 문자열을 `generate.py --prompt "..."`로 그대로 넘긴다.

## 예시

```
# 기본 생성
/openai-image "미니멀 기하학 패턴, 코랄·틸·골드"

# 특정 경로 저장
/openai-image "테크 랜딩 히어로" --output ./assets/hero.png

# 고품질 hq 모델
/openai-image "디테일한 일러스트" --model hq --size 1536x1024 --quality high

# 투명 배경 아이콘
/openai-image "사용자 아바타 아이콘" --background transparent --output ./icon.png

# 편집 모드 (전체)
/openai-image "하늘을 석양으로" --edit ./photo.png --output ./sunset.png

# 마스크 기반 inpaint
/openai-image "로고를 현대적 타이포그래피로" --edit ./src.png --mask ./mask.png

# 프롬프트 리라이터
/openai-image "고양이" --rewrite

# 스트리밍 (긴 생성의 중간 상태 확인)
/openai-image "복잡한 장면" --model hq --quality high --stream
```

## 환경 변수

- `OPENAI_API_KEY` — 필수
- `--rewrite`는 플러그인 내부 `prompt-rewriter` 서브에이전트로 처리되므로 별도 API 키가 필요 없다

## nanobanana와의 구분

빠른 응답, 마스크 편집, 투명 배경, 조밀 텍스트가 필요하면 이 커맨드. Google 생태계 연동이나 14개까지 참조 이미지 블렌딩이 필요하면 `/nanobanana`.
