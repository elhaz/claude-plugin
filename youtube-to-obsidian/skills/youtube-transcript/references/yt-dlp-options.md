# yt-dlp 자막 다운로드 옵션 상세 가이드

## 설치 방법

### Windows
```bash
# winget (권장)
winget install yt-dlp

# pip
pip install yt-dlp

# chocolatey
choco install yt-dlp
```

### macOS
```bash
# homebrew
brew install yt-dlp

# pip
pip install yt-dlp
```

### Linux
```bash
# apt (Debian/Ubuntu)
sudo apt install yt-dlp

# pip
pip install yt-dlp
```

## 기본 자막 다운로드 명령어

### 한국어 자막 다운로드
```bash
yt-dlp --write-sub --write-auto-sub --sub-lang ko --sub-format vtt --skip-download -o "00_Inbox/%(title)s [%(id)s]" "URL"
```

### 영어 자막 다운로드
```bash
yt-dlp --write-sub --write-auto-sub --sub-lang en --sub-format vtt --skip-download -o "00_Inbox/%(title)s [%(id)s]" "URL"
```

### 여러 언어 동시 다운로드
```bash
yt-dlp --write-sub --write-auto-sub --sub-lang ko,en --sub-format vtt --skip-download -o "00_Inbox/%(title)s [%(id)s]" "URL"
```

## 옵션 상세 설명

### 자막 관련 옵션

| 옵션 | 설명 |
|------|------|
| `--write-sub` | 자막 파일을 다운로드한다 |
| `--write-auto-sub` | YouTube 자동 생성 자막도 포함한다 |
| `--sub-lang LANG` | 다운로드할 자막 언어를 지정한다 (ko, en, ja 등) |
| `--sub-format FORMAT` | 자막 형식을 지정한다 (vtt, srt, ass 등) |
| `--all-subs` | 사용 가능한 모든 자막을 다운로드한다 |
| `--list-subs` | 사용 가능한 자막 목록만 표시한다 (다운로드 안 함) |

### 다운로드 제어 옵션

| 옵션 | 설명 |
|------|------|
| `--skip-download` | 영상 파일은 다운로드하지 않는다 |
| `--no-overwrites` | 기존 파일을 덮어쓰지 않는다 |
| `--no-cache-dir` | 캐시를 사용하지 않는다 |

### 출력 템플릿 옵션

| 변수 | 설명 |
|------|------|
| `%(title)s` | 영상 제목 |
| `%(id)s` | 영상 ID |
| `%(channel)s` | 채널 이름 |
| `%(upload_date)s` | 업로드 날짜 (YYYYMMDD) |
| `%(duration)s` | 영상 길이 (초) |

### 예시 출력 템플릿
```bash
# 기본 (제목 [ID])
-o "00_Inbox/%(title)s [%(id)s]"

# 채널명 포함
-o "00_Inbox/%(channel)s - %(title)s [%(id)s]"

# 날짜 포함
-o "00_Inbox/%(upload_date)s %(title)s [%(id)s]"
```

## 메타데이터 추출

### JSON 메타데이터 덤프
```bash
yt-dlp --dump-json --skip-download "URL"
```

### 유용한 JSON 필드
```json
{
  "title": "영상 제목",
  "description": "영상 설명",
  "thumbnail": "썸네일 URL",
  "channel": "채널 이름",
  "upload_date": "20250101",
  "duration": 600,
  "view_count": 1000000
}
```

### Python에서 메타데이터 추출
```python
import subprocess
import json

result = subprocess.run(
    ['yt-dlp', '--dump-json', '--skip-download', url],
    capture_output=True, text=True
)
data = json.loads(result.stdout)
title = data['title']
thumbnail = data['thumbnail']
```

## 자막 언어 코드

| 코드 | 언어 |
|------|------|
| `ko` | 한국어 |
| `en` | 영어 |
| `ja` | 일본어 |
| `zh-Hans` | 중국어 (간체) |
| `zh-Hant` | 중국어 (번체) |
| `es` | 스페인어 |
| `fr` | 프랑스어 |
| `de` | 독일어 |

## 자막 형식

| 형식 | 설명 | 확장자 |
|------|------|--------|
| `vtt` | WebVTT (권장) | .vtt |
| `srt` | SubRip | .srt |
| `ass` | Advanced SubStation Alpha | .ass |
| `json3` | YouTube JSON | .json3 |

**VTT 형식을 권장하는 이유:**
- 타임스탬프가 밀리초 단위로 정확함
- 인라인 타임스탬프 지원
- 웹 표준 형식

## 고급 사용법

### 특정 시간대만 다운로드
```bash
yt-dlp --download-sections "*00:00-05:00" --write-sub --write-auto-sub --sub-lang ko --sub-format vtt "URL"
```

### 플레이리스트 전체 자막 다운로드
```bash
yt-dlp --write-sub --write-auto-sub --sub-lang ko --sub-format vtt --skip-download -o "00_Inbox/%(playlist_title)s/%(title)s [%(id)s]" "PLAYLIST_URL"
```

### 자막이 있는지 확인만 하기
```bash
yt-dlp --list-subs "URL"
```

출력 예시:
```
Available subtitles for VIDEO_ID:
Language formats
ko       vtt, json3
en       vtt, json3 (auto-generated)
```

## 자주 사용하는 명령어 모음

```bash
# 1. 한국어 자막 다운로드 (기본)
yt-dlp --write-sub --write-auto-sub --sub-lang ko --sub-format vtt --skip-download -o "00_Inbox/%(title)s [%(id)s]" "URL"

# 2. 영어 자막 다운로드 (한국어 없을 때)
yt-dlp --write-sub --write-auto-sub --sub-lang en --sub-format vtt --skip-download -o "00_Inbox/%(title)s [%(id)s]" "URL"

# 3. 자막 목록 확인
yt-dlp --list-subs "URL"

# 4. 메타데이터만 추출
yt-dlp --dump-json --skip-download "URL"

# 5. 모든 자막 다운로드
yt-dlp --write-sub --write-auto-sub --all-subs --sub-format vtt --skip-download -o "00_Inbox/%(title)s [%(id)s]" "URL"
```
