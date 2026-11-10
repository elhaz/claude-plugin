# Obsidian Cardlink 형식 가이드

## 개요

Cardlink는 Obsidian Auto Card Link 플러그인에서 사용하는 형식으로, 웹 링크를 풍부한 미리보기 카드로 표시한다.

## 기본 형식

```markdown
```cardlink
url: https://www.youtube.com/watch?v=VIDEO_ID
title: 영상 제목
description: 영상 설명 (200자 이내)
host: www.youtube.com
favicon: https://www.youtube.com/s/desktop/626d9c6b/img/favicon_32x32.png
image: https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg
```
```

## 필드

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `url` | 필수 | 원본 URL | `https://www.youtube.com/watch?v=abc123` |
| `title` | 필수 | 페이지/영상 제목 | `Claude Code 사용법` |
| `description` | 필수 | 설명 텍스트 | `AI 코딩 도구 소개` |
| `host` | 필수 | 호스트 도메인 | `www.youtube.com` |
| `favicon` | 확인될 때만 | 파비콘 URL | (아래 참조) |
| `image` | 확인될 때만 | 썸네일/대표 이미지 URL | (아래 참조) |

> [!important] `favicon`·`image` 는 실제로 열릴 때만 넣는다 (2026-11-10)
> 주소를 짐작해 넣으면 카드에 **빈 이미지 아이콘**이 뜬다. 넣기 전에 확인하고, 안 되면 **그 줄을 통째로 뺀다**(빈 값 `image:` 도 남기지 않는다). 둘 다 없는 카드도 제목·설명·주소만으로 깔끔하게 나온다.
> ```bash
> curl -sIL -o /dev/null -w '%{http_code} %{content_type}\n' "<URL>"   # 200 image/… 여야 넣는다
> ```
> - 유튜브 썸네일 `maxresdefault.jpg` 는 영상에 따라 없다(404) → `hqdefault.jpg` 로 바꾸거나 뺀다
> - 블로그·뉴스의 `og:image` 는 만료 서명 URL 이거나 핫링크 차단일 수 있다 → 확인이 안 되면 뺀다
> - 볼트 쪽 같은 규칙: `06_Metadata/Reference/Obsidian 마크다운 작성 가이드.md` 「웹 링크 추가」

## YouTube 전용 값

### 파비콘 URL
```
https://www.youtube.com/s/desktop/626d9c6b/img/favicon_32x32.png
```

### 썸네일 URL 패턴
```
https://i.ytimg.com/vi/VIDEO_ID/maxresdefault.jpg
```

VIDEO_ID 부분에 실제 영상 ID를 넣는다.

### 썸네일 해상도 옵션
| URL 패턴 | 해상도 |
|----------|--------|
| `maxresdefault.jpg` | 1280x720 (최고 화질) |
| `sddefault.jpg` | 640x480 |
| `hqdefault.jpg` | 480x360 |
| `mqdefault.jpg` | 320x180 |
| `default.jpg` | 120x90 |

## YAML 문법 주의사항

### 따옴표 사용 금지

Cardlink 내부는 YAML 형식이므로 따옴표 처리에 주의해야 한다.

**오류 예시:**
```yaml
title: "니트 보호하려고 쓴 '세탁망'..."  # YAML 파싱 오류
description: "이것은 '인용'이 들어간 설명"  # YAML 파싱 오류
```

**올바른 예시:**
```yaml
title: 니트 보호하려고 쓴 세탁망 충격적 배신
description: 이것은 인용이 들어간 설명
```

### 특수문자 처리

제거하거나 변환해야 하는 문자:
- 작은따옴표 (`'`) → 제거
- 큰따옴표 (`"`) → 제거
- 말줄임표 (`...`) → 제거
- 콜론 (`:`) → ` -`로 변환
- 줄바꿈 → 공백으로 변환
- **첫 글자가 YAML 기호**(`[` `{` `@` `&` `*` `!` `|` `>` `%` `` ` `` `#`) → 대괄호·중괄호는 소괄호로, 그 밖의 기호는 앞에 낱말을 붙인다
  - `title: [속보] Fable 5.2 출시` → YAML 이 목록으로 읽어 카드가 깨진다 → `title: (속보) Fable 5.2 출시`
  - `title: @Transactional 붙였는데` → `@` 는 예약 기호라 오류 → `title: Spring @Transactional 붙였는데`

### Python 변환 함수

```python
def sanitize_yaml_string(text):
    """YAML 안전 문자열로 변환"""
    if not text:
        return ''
    # 따옴표, 말줄임표 등 특수문자 제거
    text = text.replace('"', '').replace("'", '').replace('...', '')
    text = text.replace(':', ' -').replace('\n', ' ').replace('\r', '')
    # 연속 공백 정리
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    # 첫 글자가 YAML 기호면 깨진다 — 대괄호·중괄호는 소괄호로 바꾼다
    if text.startswith('['):
        text = text.replace('[', '(', 1).replace(']', ')', 1)
    elif text.startswith('{'):
        text = text.replace('{', '(', 1).replace('}', ')', 1)
    # 그 밖의 기호(@ & * ! | > % ` #)로 시작하면 손으로 낱말을 붙인다 (예: Spring @Transactional)
    if text[:1] in tuple('@&*!|>%`#'):
        raise ValueError(f'첫 글자가 YAML 기호: {text[:20]} — 앞에 낱말을 붙일 것')
    return text
```

## 메타데이터 추출 방법

### yt-dlp 사용 (권장)

```bash
yt-dlp --dump-json --skip-download "URL"
```

JSON 필드 매핑:
- `title` → title
- `description` → description (처음 200자)
- `thumbnail` → image

### Python 코드

```python
import subprocess
import json

def get_video_metadata(video_url):
    result = subprocess.run(
        ['yt-dlp', '--dump-json', '--skip-download', video_url],
        capture_output=True, text=True, encoding='utf-8'
    )
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return {
            'title': data.get('title', ''),
            'description': data.get('description', '')[:200],
            'thumbnail': data.get('thumbnail', ''),
            'channel': data.get('channel', '')
        }
    return None
```

## 완성 예시

### 입력 (yt-dlp JSON)
```json
{
  "title": "Claude Code: AI 코딩의 '새로운' 시대",
  "description": "이 영상에서는 Claude Code의 핵심 기능을 소개합니다...",
  "thumbnail": "https://i.ytimg.com/vi/abc123/maxresdefault.jpg",
  "id": "abc123"
}
```

### 출력 (Cardlink)
```markdown
```cardlink
url: https://www.youtube.com/watch?v=abc123
title: Claude Code AI 코딩의 새로운 시대
description: 이 영상에서는 Claude Code의 핵심 기능을 소개합니다
host: www.youtube.com
favicon: https://www.youtube.com/s/desktop/626d9c6b/img/favicon_32x32.png
image: https://i.ytimg.com/vi/abc123/maxresdefault.jpg
```
```

## 일반 웹페이지 메타데이터

YouTube가 아닌 일반 웹페이지의 경우 Open Graph 태그에서 추출한다:

```html
<meta property="og:title" content="페이지 제목">
<meta property="og:description" content="페이지 설명">
<meta property="og:image" content="대표 이미지 URL">
<link rel="icon" href="파비콘 URL">
```

메타데이터 우선순위:
1. Open Graph (`og:*`)
2. Twitter Card (`twitter:*`)
3. Schema.org
4. 일반 HTML 메타태그

## Obsidian에서의 표시

Cardlink가 올바르게 작성되면 Obsidian에서 다음과 같이 표시된다:

```
┌─────────────────────────────────────┐
│ [썸네일 이미지]                      │
├─────────────────────────────────────┤
│ 🌐 www.youtube.com                  │
│ 영상 제목                            │
│ 영상 설명 텍스트...                  │
└─────────────────────────────────────┘
```

클릭하면 원본 URL로 이동한다.
