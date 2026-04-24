---
name: generate
version: 1.3.0
description: OpenAI gpt-image-1.5 / gpt-image-1-mini 기반 이미지 생성 및 편집 스킬(조직 인증 완료 시 gpt-image-2도 지원). 사용자가 "openai로 이미지 생성", "gpt-image", "빠른 이미지 생성", "투명 배경 로고/아이콘", "마스크 기반 이미지 편집", "inpaint", "outpaint" 를 언급하거나, Gemini/Nano Banana보다 더 빠른 응답과 정밀한 편집이 필요한 경우 호출한다.
---

# OpenAI Image Generation (gpt-image-1.5 / gpt-image-1-mini, optional gpt-image-2)

OpenAI의 `gpt-image` 계열 모델을 사용해 이미지를 생성·편집한다. 자매 플러그인 `nanobanana`(Google Gemini)와 비교해 **응답 속도가 빠르고 마스크 기반 정밀 편집과 투명 배경을 지원**한다.

## Prerequisites

- `OPENAI_API_KEY` 환경변수 필수
- `uv`가 설치되어 있어야 함 (PEP 723 인라인 의존성 자동 설치)
- 프롬프트 확장(rewrite)이 필요할 때는 플러그인 내부 `prompt-rewriter` 서브에이전트가 자동 호출되며 별도 API 키는 필요 없다

## 모델 선택 가이드

| 별칭 | 실제 ID | 조직 인증 | 언제 쓸지 |
|------|---------|----------|----------|
| `fast` (기본) | `gpt-image-1-mini` | 불필요 | 반복 iteration, 드래프트, 속도·비용 우선 |
| `hq` | `gpt-image-1.5` | 불필요 | 최종 결과물, 조밀한 텍스트(로고·다이어그램), 복잡한 장면. 일반 계정에서 바로 사용 가능 |
| `v2` | `gpt-image-2` | **필수** | 최신 플래그십. 다국어 조밀 텍스트·2K/4K·Thinking 모드. 단, 조직 인증(신분증 촬영·본인 확인) 완료한 계정에서만 호출 가능. 미인증 계정은 403/400 에러 |

platform.openai.com에서 제공되는 현행 이미지 모델: `gpt-image-1`, `gpt-image-1-mini`, `gpt-image-1.5`, `gpt-image-2`, `gpt-image-2-2026-04-21`(스냅샷). 스냅샷 고정이 필요하면 원시 ID를 직접 지정한다(예: `--model gpt-image-2-2026-04-21`).

> 조직 인증이 귀찮거나 차단된 경우 `hq`(gpt-image-1.5)를 사용하면 본인 확인 없이 고품질 결과를 얻을 수 있다.

## nanobanana와의 구분

| 상황 | 추천 |
|------|------|
| 응답 속도가 중요 (~30초 이내) | **openai-image** |
| 마스크 기반 정밀 편집 (inpaint/outpaint) | **openai-image** |
| 투명 배경 PNG/WebP | **openai-image** |
| 조밀한 텍스트 렌더링 (로고, 포스터, 인포그래픽) | **openai-image** |
| Google 생태계 연동, 대량 배치 | nanobanana |
| 14개까지 참조 이미지 블렌딩 | nanobanana |

## 생성 워크플로우

### Step 1: 기본 생성

스크립트 위치: `${SKILL_DIR}/scripts/generate.py`

```bash
uv run "${SKILL_DIR}/scripts/generate.py" \
  --prompt "미니멀 기하학 로고, 코랄과 틸 색상" \
  --output ./logo.png
```

기본값: `--model fast`, `--size 1024x1024`, `--quality medium`, `--format webp` (용량이 작아 프론트엔드 에셋에 유리. 투명 배경이 필요하면 `--background transparent`는 webp에서도 동작).

주요 옵션:

| 옵션 | 값 |
|------|-----|
| `--model` | `fast` / `hq` / 원시 모델 ID |
| `--size` | `1024x1024` / `1536x1024` / `1024x1536` / `auto` |
| `--quality` | `low` / `medium` / `high` / `auto` |
| `--background` | `auto` / `transparent` / `opaque` |
| `--format` | `png` / `jpeg` / `webp` (기본 `webp` — 용량 절감) |
| `--n` | 1~4 |
| `--timeout` | 초 단위 (기본 120) |
| `--stream` | 중간 partial_images 로그 |

> 참고: 이전 버전에 있던 `--rewrite` CLI 플래그는 제거되었다. 프롬프트 확장은 `prompt-rewriter` 에이전트가 담당한다.

### Step 2: 고품질 모델 사용

최종 에셋이 필요할 때:

```bash
uv run "${SKILL_DIR}/scripts/generate.py" \
  --prompt "A detailed hero illustration for a fintech landing page" \
  --output ./hero.png \
  --model hq --size 1536x1024 --quality high
```

### Step 3: 투명 배경 (로고·아이콘)

```bash
uv run "${SKILL_DIR}/scripts/generate.py" \
  --prompt "A minimalist gear icon in coral color" \
  --output ./icon.png \
  --background transparent --format png
```

`--background transparent`는 PNG/WebP 포맷에서만 유의미하다.

### Step 4: 편집 모드 (전체 이미지)

마스크 없이 전체 이미지를 자연어로 수정:

```bash
uv run "${SKILL_DIR}/scripts/generate.py" \
  --prompt "Change the sky to a dramatic sunset" \
  --output ./edited.png \
  --edit ./original.png
```

### Step 5: 마스크 기반 정밀 편집 (inpaint/outpaint)

마스크 PNG의 **투명(알파=0) 영역이 편집 대상**이다:

```bash
uv run "${SKILL_DIR}/scripts/generate.py" \
  --prompt "Replace the logo with a modern typography treatment" \
  --output ./inpainted.png \
  --edit ./original.png --mask ./mask.png
```

이 기능이 Gemini 대비 가장 강력한 차별점이다.

### Step 6: 프롬프트 리라이터 (서브에이전트 경유)

사용자 프롬프트가 짧거나 모호할 때(예: `cat`, `로고`, `히어로 이미지` 같이 단어 수준) Claude는 **Agent 도구로 `prompt-rewriter` 서브에이전트를 먼저 호출**해 6요소(Subject·Style·Colors·Mood·Composition·Technical)가 담긴 영문 상세 프롬프트를 받은 뒤, 그 결과를 `--prompt` 인자로 `generate.py`에 전달한다.

호출 예시 (Claude 내부 워크플로우):

1. 사용자 입력: `/openai-image "cat" --rewrite`
2. Claude가 Agent 도구로 `subagent_type: prompt-rewriter` 호출. 프롬프트로 원본 `cat`과 용도 힌트 전달
3. 에이전트가 확장된 영문 단락 반환
4. Claude가 해당 확장 프롬프트를 `--prompt` 값으로 `generate.py` 실행

`generate.py` 자체는 LLM 호출을 하지 않는다. 별도 API 키(ANTHROPIC_API_KEY 등)도 불필요하다. `--rewrite`는 CLI 플래그가 아니라 **호출 측이 prompt-rewriter 에이전트를 먼저 돌릴지 판단하는 힌트**다.

### Step 7: 스트리밍 (중간 진행 알림)

요청이 오래 걸릴 때 체감 대기시간을 줄이기 위해:

```bash
uv run "${SKILL_DIR}/scripts/generate.py" \
  --prompt "..." --output ./out.png --stream
```

stderr로 `중간 이미지 수신 #1`, `#2` 로그가 흐른 뒤 최종 이미지가 저장된다.

## 프롬프트 작성 팁

좋은 프롬프트에 포함할 요소:
1. **Subject**: 무엇을 담는가
2. **Style**: 아트 스타일 (minimalist, photorealistic, illustration 등)
3. **Colors**: 구체 색상 팔레트
4. **Mood/Lighting**: 분위기와 조명
5. **Composition**: 구도, 앵글, 여백
6. **Technical**: 해상도, 디테일, 렌즈 느낌

짧게 쓰고 싶다면 `--rewrite`를 사용하자.

## 오류 처리

- `OPENAI_API_KEY` 없음 → 환경변수 설정 안내
- 타임아웃 → `--timeout` 값을 늘리거나 `--quality low`·`--model fast`로 재시도
- 편집 대상/마스크 파일 없음 → 경로 재확인

## 관련 문서

- 플러그인 루트: [../../CLAUDE.md](../../CLAUDE.md)
- 슬래시 커맨드: [../../commands/openai-image.md](../../commands/openai-image.md)
