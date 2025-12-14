# YouTube to Obsidian

YouTube 자막을 Obsidian 스타일 마크다운 문서로 변환하는 Claude Code 플러그인입니다.

## 기능

- YouTube URL에서 자막(VTT) 자동 다운로드
- 한국어 자막 우선, 없으면 영어 자막 다운로드 후 번역
- VTT를 Obsidian 마크다운 형식으로 변환
- Obsidian cardlink 형식으로 영상 정보 삽입
- 중복 텍스트 자동 제거
- 노이즈 제거 ([음악], Ah. 등)

## 설치

### 방법 1: 글로벌 플러그인으로 설치
```bash
# 플러그인 디렉토리로 복사
cp -r youtube-to-obsidian ~/.claude/plugins/
```

### 방법 2: 프로젝트 로컬 플러그인으로 설치
```bash
# 프로젝트 루트에 .claude-plugin 디렉토리로 복사
cp -r youtube-to-obsidian /path/to/project/.claude-plugin/
```

## 사전 요구사항

- **yt-dlp**: YouTube 자막 다운로드용
  ```bash
  # Windows (winget)
  winget install yt-dlp

  # macOS (homebrew)
  brew install yt-dlp

  # pip
  pip install yt-dlp
  ```

- **Python 3.8+**: 변환 스크립트 실행용
- **uv** (권장): Python 패키지 관리

## 사용법

### 명령어
```
/youtube-extract <YouTube_URL>
```

### 예시
```
/youtube-extract https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 출력
- 변환된 마크다운 파일이 `00_Inbox/` 폴더에 생성됩니다.
- 파일명: `[영상제목].md`

## 워크플로우

1. yt-dlp로 VTT 자막 다운로드
2. vtt_to_markdown.py로 마크다운 변환
3. Obsidian cardlink 형식으로 영상 정보 삽입
4. 중복 텍스트 및 노이즈 제거
5. 00_Inbox/에 저장
6. 원본 VTT 파일 삭제

## 플러그인 구조

```
youtube-to-obsidian/
├── .claude-plugin/
│   └── plugin.json          # 플러그인 매니페스트
├── commands/
│   └── youtube-extract.md   # /youtube-extract 커맨드
├── skills/
│   └── youtube-transcript/
│       ├── SKILL.md         # 스킬 메인 파일
│       └── references/      # 상세 참조 문서
│           ├── yt-dlp-options.md
│           ├── cardlink-format.md
│           └── troubleshooting.md
├── scripts/
│   └── vtt_to_markdown.py   # VTT 변환 스크립트
└── README.md
```

## 스킬 트리거

다음 질문들이 스킬을 활성화합니다:
- "YouTube 자막 추출해줘"
- "YouTube 영상을 마크다운으로 변환"
- "yt-dlp 사용법 알려줘"
- "VTT 파일 변환 방법"

## 라이선스

MIT License
