# 문제 해결 가이드

## 일반적인 문제

### 1. yt-dlp 명령어를 찾을 수 없음

**증상:**
```
'yt-dlp'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결 방법:**

Windows:
```bash
# winget으로 설치
winget install yt-dlp

# 또는 pip으로 설치
pip install yt-dlp
```

macOS:
```bash
brew install yt-dlp
```

Linux:
```bash
sudo apt install yt-dlp
# 또는
pip install yt-dlp
```

설치 확인:
```bash
yt-dlp --version
```

### 2. 자막이 없는 영상

**증상:**
```
WARNING: [youtube] VIDEO_ID: There are no subtitles for the requested languages
```

**해결 방법:**

1. 사용 가능한 자막 확인:
   ```bash
   yt-dlp --list-subs "URL"
   ```

2. 다른 언어로 시도:
   ```bash
   yt-dlp --write-sub --write-auto-sub --sub-lang en --sub-format vtt --skip-download "URL"
   ```

3. 모든 자막 다운로드:
   ```bash
   yt-dlp --write-sub --write-auto-sub --all-subs --sub-format vtt --skip-download "URL"
   ```

**참고:** 모든 영상에 자막이 있는 것은 아님. 특히 라이브 스트림이나 오래된 영상은 자막이 없을 수 있음.

### 3. Python/uv 관련 오류

**증상:**
```
'uv' is not recognized as an internal or external command
```

**해결 방법:**

uv 설치:
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

uv 대신 python 직접 사용:
```bash
PYTHONIOENCODING=utf-8 python scripts/vtt_to_markdown.py "파일경로"
```

### 4. 한글 인코딩 오류

**증상:**
```
UnicodeEncodeError: 'cp949' codec can't encode character
```

**해결 방법:**

환경 변수 설정:
```bash
PYTHONIOENCODING=utf-8 uv run scripts/vtt_to_markdown.py "파일경로"
```

Windows PowerShell:
```powershell
$env:PYTHONIOENCODING = "utf-8"
uv run scripts/vtt_to_markdown.py "파일경로"
```

### 5. VTT 파일을 찾을 수 없음

**증상:**
```
[오류] 파일을 찾을 수 없습니다: 경로
```

**해결 방법:**

1. 파일 존재 확인:
   ```bash
   ls 00_Inbox/*.vtt
   ```

2. 파일 경로에 특수문자가 있는지 확인
3. 절대 경로 사용:
   ```bash
   uv run scripts/vtt_to_markdown.py "D:/SynologyDrive/XVault/00_Inbox/파일명.vtt"
   ```

### 6. Cardlink YAML 파싱 오류

**증상:**
Obsidian에서 cardlink가 제대로 표시되지 않음

**원인:**
title이나 description에 따옴표나 특수문자가 포함됨

**해결 방법:**

수동으로 따옴표 제거:
```yaml
# 오류
title: "제목에 '따옴표'가 있음"

# 수정
title: 제목에 따옴표가 있음
```

### 7. 네트워크 오류

**증상:**
```
ERROR: Unable to download webpage
```

**해결 방법:**

1. 인터넷 연결 확인
2. URL이 올바른지 확인
3. 프록시 설정 확인:
   ```bash
   yt-dlp --proxy "http://proxy:port" "URL"
   ```

### 8. 영상이 차단됨

**증상:**
```
ERROR: Video unavailable. This video is not available in your country
```

**해결 방법:**

VPN 사용 또는 프록시 설정:
```bash
yt-dlp --proxy "socks5://127.0.0.1:1080" "URL"
```

## 스크립트 관련 문제

### 중복이 완전히 제거되지 않음

VTT 자막의 특성상 일부 중복이 남을 수 있음. 수동으로 정리하거나 스크립트의 중복 제거 임계값 조정.

### 타임스탬프가 잘못됨

VTT 파일 형식이 표준과 다를 경우 발생. 파일을 직접 확인하여 형식 확인.

### 메타데이터 가져오기 실패

yt-dlp가 영상 정보를 가져오지 못하는 경우:
```
[경고] 메타데이터 가져오기 실패
```

해결: cardlink 대신 일반 링크로 대체됨. 수동으로 cardlink 추가 가능.

## 디버깅 팁

### 1. 상세 로그 출력

```bash
yt-dlp -v --write-sub --write-auto-sub --sub-lang ko --sub-format vtt --skip-download "URL"
```

### 2. 스크립트 디버깅

```python
# 스크립트 수정하여 디버그 출력 추가
print(f"[DEBUG] 파싱된 엔트리 수: {len(entries)}")
```

### 3. VTT 파일 직접 확인

```bash
head -50 "00_Inbox/파일명.vtt"
```

## 자주 묻는 질문

### Q: 플레이리스트 전체를 처리할 수 있나요?

A: yt-dlp는 플레이리스트를 지원하지만, 변환 스크립트는 개별 파일만 처리함. 플레이리스트의 각 영상을 개별적으로 처리해야 함.

### Q: 자막 언어를 자동으로 감지할 수 있나요?

A: `yt-dlp --list-subs`로 확인 후 적절한 언어를 선택. 자동 감지는 지원하지 않음.

### Q: SRT 형식도 지원하나요?

A: 현재 스크립트는 VTT 형식만 지원. SRT를 사용하려면 스크립트 수정 필요.

### Q: 번역 기능이 내장되어 있나요?

A: 아니오. 영어 자막인 경우 Claude에게 번역을 요청해야 함.
