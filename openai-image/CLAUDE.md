# CLAUDE.md

이 파일은 Claude Code가 이 플러그인 작업 시 참고하는 가이드다.

## 개요

`openai-image`는 OpenAI 이미지 생성/편집 API(`gpt-image-1.5`, `gpt-image-1-mini`)를 사용하는 Claude Code 플러그인이다. `/openai-image` 슬래시 커맨드 또는 이미지 생성 요청을 통해 호출된다.

자매 플러그인 `nanobanana`(Google Gemini 기반)와 공존하며, **속도·마스크 기반 정밀 편집·투명 배경·조밀한 텍스트 렌더링**이 필요한 경우 이 플러그인을 사용한다.

## 실행 방법

```bash
uv run skills/generate/scripts/generate.py \
  --prompt "이미지 설명" \
  --output "출력경로.png"
```

주요 옵션:
- `--model`: `fast`(기본, `gpt-image-1-mini`) 또는 `hq`(`gpt-image-1.5`). 원시 모델 ID를 직접 넣어도 됨
- `--size`: `1024x1024`(기본) / `1536x1024` / `1024x1536` / `auto`
- `--quality`: `low` / `medium`(기본) / `high` / `auto`
- `--background`: `auto`(기본) / `transparent` / `opaque`
- `--format`: `webp`(기본, 용량 절감) / `png` / `jpeg`
- `--edit <image>`: 편집 모드. `--mask <image>` 선택적 동반
- `--timeout <초>`: 기본 120초
- `--stream`: partial_images로 중간 진행 알림

프롬프트 확장(rewrite)은 CLI 플래그가 아니라 플러그인 내부 **`prompt-rewriter` 서브에이전트**가 담당한다. Claude가 Agent 도구로 해당 에이전트를 먼저 호출해 상세 프롬프트를 받은 뒤 `generate.py`를 실행한다.

## 필수 환경변수

- `OPENAI_API_KEY` — 필수 (generate.py 실행용)

## 아키텍처

```
openai-image/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── prompt-rewriter.md        # 짧은 프롬프트를 상세 영문으로 확장하는 경량 에이전트
├── commands/
│   └── openai-image.md           # /openai-image 슬래시 커맨드
└── skills/
    └── generate/
        ├── SKILL.md              # Claude가 읽는 스킬 가이드
        └── scripts/
            └── generate.py       # 생성·편집 메인 스크립트 (PEP 723)
```

의존성은 PEP 723 인라인 메타데이터로 관리되어 `uv run`이 자동 설치한다. 프롬프트 확장은 Anthropic SDK가 아니라 Claude Code의 Agent 도구를 통해 서브에이전트로 처리되므로 별도 API 키나 네트워크 호출이 필요 없다.

## 관련 문서

- 스킬 상세: [skills/generate/SKILL.md](skills/generate/SKILL.md)
- 슬래시 커맨드: [commands/openai-image.md](commands/openai-image.md)
