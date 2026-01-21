---
name: nanobanana
description: Gemini AI 이미지 생성 - 프롬프트로 이미지를 생성합니다
argument-hint: <prompt> [--output path] [--aspect ratio] [--model flash|pro]
allowed-tools:
  - Bash
  - Read
  - Write
---

# Nano Banana Pro - 이미지 생성 커맨드

Google Gemini 모델을 사용하여 이미지를 생성한다.

## 사용 방법

```
/nanobanana "이미지 설명 프롬프트"
/nanobanana "프롬프트" --output ./path/to/image.png
/nanobanana "프롬프트" --aspect landscape --model pro
```

## 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `--output` | 출력 파일 경로 (PNG) | `./generated-image.png` |
| `--aspect` | 비율: square, landscape, portrait | square |
| `--model` | 모델: flash (빠름), pro (고품질) | flash |
| `--size` | 해상도 (pro만): 1K, 2K, 4K | 1K |
| `--reference` | 참조 이미지 경로 | - |

## 실행 방법

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/generate/scripts/image.py" \
  --prompt "프롬프트" \
  --output "출력경로.png" \
  [--aspect square|landscape|portrait] \
  [--model flash|pro] \
  [--size 1K|2K|4K] \
  [--reference "참조이미지.png"]
```

## 처리 워크플로우

1. 사용자 인자에서 프롬프트와 옵션 파싱
2. 출력 경로가 지정되지 않으면 현재 디렉토리에 `generated-image.png`로 저장
3. Python 스크립트 실행:
   ```bash
   uv run "${CLAUDE_PLUGIN_ROOT}/skills/generate/scripts/image.py" \
     --prompt "<프롬프트>" \
     --output "<출력경로>"
   ```
4. 생성 완료 후 파일 경로 안내

## 예시

```
# 기본 이미지 생성
/nanobanana "미니멀한 기하학적 패턴, 코랄과 틸 색상"

# 특정 경로에 저장
/nanobanana "테크 랜딩페이지용 히어로 이미지" --output ./assets/hero.png

# 고품질 Pro 모델 사용
/nanobanana "세밀한 일러스트레이션" --model pro --size 2K

# 가로 비율로 생성
/nanobanana "배너 이미지" --aspect landscape

# 참조 이미지 기반 생성
/nanobanana "비슷한 스타일로 따뜻한 색상" --reference ./reference.png
```

## 프롬프트 작성 팁

좋은 프롬프트에 포함할 요소:
1. **주제**: 이미지가 무엇을 표현하는지
2. **스타일**: 미니멀, 추상, 사실적, 일러스트 등
3. **색상**: 구체적인 색상 팔레트
4. **분위기**: 전문적, 밝은, 우아한, 대담한 등
5. **용도**: 히어로 이미지, 아이콘, 텍스처, 배경 등

## 환경 변수

`GEMINI_API_KEY` 환경 변수가 설정되어 있어야 한다.

## 오류 처리

- API 키 없음: `GEMINI_API_KEY` 환경 변수 설정 안내
- 생성 실패: 오류 메시지와 함께 재시도 권장
- 파일 저장 실패: 경로 권한 확인 안내
