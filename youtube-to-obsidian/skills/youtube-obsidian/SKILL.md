---
name: YouTube Transcript to Obsidian
description: 이 스킬은 사용자가 "YouTube 자막 추출", "YouTube 영상을 마크다운으로", "yt-dlp 사용법", "VTT 변환", "YouTube 자막 다운로드", "vtt_to_markdown 사용법", "YouTube Obsidian 문서화"를 요청할 때 사용한다. YouTube 자막을 Obsidian 스타일 마크다운 문서로 변환하는 워크플로우 가이드를 제공한다.
version: 1.0.2
---

# YouTube 자막 → Obsidian 문서 변환 가이드

YouTube 영상의 자막(VTT)을 Obsidian 스타일 마크다운 문서로 변환하는 워크플로우를 제공한다.

## 개요

이 스킬은 다음 작업을 지원한다:
- yt-dlp를 사용한 YouTube 자막 다운로드
- VTT 파일을 Obsidian 마크다운으로 변환
- Obsidian cardlink 형식으로 영상 정보 삽입
- 중복 텍스트 및 노이즈 자동 제거
- **Obsidian 스타일로 문서 재구성** (콜아웃, 표, 내부링크, 구조화된 섹션)
- **임시 폴더에서 작업 후 최종 파일만 Vault로 이동**
- **여러 URL 병렬 처리**

## 핵심 원칙

> [!important] 작업 원칙
> 1. **임시 폴더 사용**: Obsidian이 파일을 자동 수정하는 것을 방지하기 위해, 모든 중간 작업은 임시 폴더에서 수행하고, 최종 완성된 파일만 `00_Inbox/`로 이동
> 2. **병렬 처리**: 여러 URL이 제공되면 각 URL을 별도의 서브에이전트에서 병렬로 처리

## 빠른 시작

### 명령어 사용 (권장)

```
/youtube-extract <YouTube_URL>
```

여러 URL을 한 번에 처리:
```
/youtube-extract URL1 URL2 URL3
```

이 명령어는 자막 다운로드부터 Obsidian 스타일 재구성까지 모든 과정을 자동화한다.

### 수동 워크플로우

전체 과정을 수동으로 실행하려면:

1. **임시 폴더 생성**
   ```bash
   # Windows 환경 (Git Bash/MSYS)
   WORK_DIR="$USERPROFILE/AppData/Local/Temp/youtube-obsidian-$(date +%s)"
   mkdir -p "$WORK_DIR"
   ```

2. **자막 다운로드** (임시 폴더에)
   ```bash
   # 한국어 자막 우선
   yt-dlp --write-sub --write-auto-sub --sub-lang ko --sub-format vtt --skip-download -o "$WORK_DIR/%(title)s [%(id)s]" "URL"

   # 한국어 없으면 영어
   yt-dlp --write-sub --write-auto-sub --sub-lang en --sub-format vtt --skip-download -o "$WORK_DIR/%(title)s [%(id)s]" "URL"
   ```

3. **마크다운 변환** (임시 폴더에서)

   **방법 A: Claude가 직접 VTT 파싱 (권장)**
   - VTT 파일을 Read 도구로 읽어서 직접 마크다운으로 변환
   - 타임스탬프 추출, 중복 제거, 노이즈 제거를 Claude가 처리

   **방법 B: 변환 스크립트 사용**
   ```bash
   VTT_FILE=$(ls -t "$WORK_DIR"/*.vtt | head -1)
   # 스크립트 경로 탐색 (플러그인 설치 위치에 따라 다를 수 있음)
   SCRIPT_PATH=$(find "$USERPROFILE/.claude" -name "vtt_to_markdown.py" 2>/dev/null | head -1)
   PYTHONIOENCODING=utf-8 uv run "$SCRIPT_PATH" "$VTT_FILE" --delete-vtt
   ```

4. **영어 자막 번역** (필요시)
   - Claude에게 임시 폴더의 마크다운 파일 번역 요청

5. **Obsidian 스타일로 재구성** (핵심 단계)
   - 타임스탬프별 자막을 주제별 섹션으로 재구성
   - 콜아웃 추가: `> [!important]`, `> [!note]`, `> [!warning]`
   - 표 활용: 비교, 목록, 통계 정보
   - 내부 링크: `[[인물명]]`, `[[기관명]]`, `[[개념]]`
   - 개요 섹션 추가
   - 태그 상세화: `#유튜브 #주제 #세부주제`

6. **최종 파일 이동**
   ```bash
   MD_FILE=$(ls -t "$WORK_DIR"/*.md | head -1)
   mv "$MD_FILE" "00_Inbox/"
   rm -rf "$WORK_DIR"
   ```

## yt-dlp 필수 옵션

| 옵션 | 설명 |
|------|------|
| `--write-sub` | 자막 파일 다운로드 |
| `--write-auto-sub` | 자동 생성 자막 포함 |
| `--sub-lang ko` | 한국어 자막 지정 |
| `--sub-format vtt` | VTT 형식으로 다운로드 |
| `--skip-download` | 영상 다운로드 생략 |
| `-o "경로/%(title)s [%(id)s]"` | 출력 파일명 템플릿 |

자세한 yt-dlp 옵션은 `references/yt-dlp-options.md` 참조.

## 출력 형식

### 마크다운 구조

```markdown
---
생성일: YYYY-MM-DD
마지막수정일: YYYY-MM-DD
---

# 영상 제목

## 영상 정보

\`\`\`cardlink
url: https://www.youtube.com/watch?v=VIDEO_ID
title: 영상 제목
description: 영상 설명
host: www.youtube.com
favicon: https://www.youtube.com/favicon.ico
image: https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg
\`\`\`

- **언어**: 한국어 (자동 생성 자막)

## 자막 내용

**[00:00.00]** 첫 번째 자막 텍스트

**[00:05.23]** 두 번째 자막 텍스트

---

**태그**: #유튜브 #자막
```

### Cardlink 형식

Obsidian Auto Card Link 플러그인과 호환되는 형식이다.

필수 필드:
- `url`: YouTube URL
- `title`: 영상 제목 (따옴표 없이)
- `description`: 영상 설명 (따옴표 없이, 200자 제한)
- `host`: www.youtube.com
- `favicon`: YouTube 파비콘 URL
- `image`: 썸네일 URL

자세한 cardlink 형식은 `references/cardlink-format.md` 참조.

## 자동 처리 기능

### 중복 제거

VTT 자막의 특성상 발생하는 중복을 자동 제거:
- 완전히 동일한 텍스트
- 이전 텍스트에 포함된 텍스트
- 부분 겹침 (5글자 이상)

### 노이즈 제거

자동으로 제거되는 항목:
- `[음악]`, `[Music]`
- `[박수]`, `[Applause]`
- `Ah.` 등 의미 없는 소리

### 타임스탬프 형식

`HH:MM:SS.mmm` → `MM:SS.ss` 형식으로 변환하여 가독성 향상.

## Obsidian 스타일 재구성 가이드

단순 VTT 변환 후 반드시 Obsidian 스타일로 재구성해야 한다.

### 재구성 원칙

1. **구조화**: 타임스탬프 나열 → 주제별 섹션 (H2, H3)
2. **강조**: 핵심 내용에 콜아웃 적용
3. **연결**: 주요 개념에 내부 링크 `[[]]`
4. **정리**: 비교/목록 정보는 표로 변환
5. **요약**: 상단에 개요 섹션 추가

### 콜아웃 활용

```markdown
> [!important] 핵심 포인트
> 가장 중요한 내용

> [!note] 참고
> 배경 정보나 부연 설명

> [!warning] 주의
> 경고나 위험 요소

> [!quote] 인용
> 영상에서 인용할 만한 문구
```

### 내부 링크 적용 대상

- 인물: `[[홍길동]]`, `[[일론 머스크]]`
- 기관: `[[삼성전자]]`, `[[미국 연준]]`, `[[UN]]`
- 개념: `[[인플레이션]]`, `[[양적완화]]`, `[[GDP]]`
- 지역: `[[미국]]`, `[[중국]]`, `[[서울]]`

### 재구성 예시

**변환 전:**
```
**[00:14.01]** 2023년 미얀마에 본사를 둔...
**[00:17.02]** 로얄 슌 레이의 대표들이...
```

**재구성 후:**
```markdown
## 미얀마-북한 무기 거래

2023년 [[미얀마]] 기업 로얄 슌 레이의 대표들이 [[북한]]의
[[조선광업개발무역회사]]와 베이징에서 회동했다.

> [!important] 핵심 거래
> 공중폭탄 유도 키트 공급 합의
```

## 병렬 처리

여러 URL이 제공된 경우:
- Task 도구를 사용하여 각 URL을 별도의 서브에이전트에서 병렬 처리
- `run_in_background: true` 옵션으로 병렬 실행
- 모든 서브에이전트 완료 후 결과 수집하여 보고

## 문제 해결

일반적인 문제와 해결 방법은 `references/troubleshooting.md` 참조.

### 빠른 점검

1. **yt-dlp 설치 확인**: `yt-dlp --version`
2. **Python/uv 확인**: `uv --version`
3. **임시 폴더 확인**: `ls "$USERPROFILE/AppData/Local/Temp/youtube-obsidian-"*`

## 참고 자료

### 참조 파일

- **`references/yt-dlp-options.md`** - yt-dlp 상세 옵션 및 사용법
- **`references/cardlink-format.md`** - Obsidian cardlink 형식 상세 가이드
- **`references/troubleshooting.md`** - 문제 해결 가이드

### 스크립트

- **`scripts/vtt_to_markdown.py`** - VTT → 마크다운 변환 스크립트 (선택사항, Claude가 직접 파싱 가능)
