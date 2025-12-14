# Claude Code Plugins

Claude Code용 개인 플러그인 모음입니다.

## 플러그인 목록

| 플러그인 | 설명 | 상태 |
|---------|------|------|
| [youtube-to-obsidian](./youtube-to-obsidian/) | YouTube 자막을 Obsidian 스타일 마크다운으로 변환 | ✅ 완료 |

## 설치 방법

### 글로벌 설치 (모든 프로젝트에서 사용)

```bash
# 원하는 플러그인 폴더를 ~/.claude/plugins/에 복사
cp -r youtube-to-obsidian ~/.claude/plugins/
```

### 프로젝트 로컬 설치

```bash
# 프로젝트 루트의 .claude-plugin/ 디렉토리로 복사
cp -r youtube-to-obsidian /path/to/project/.claude-plugin/
```

## 플러그인 구조

각 플러그인은 다음 구조를 따릅니다:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json      # 플러그인 매니페스트
├── commands/            # 슬래시 커맨드 정의
├── skills/              # 스킬 정의
├── scripts/             # 헬퍼 스크립트
└── README.md            # 플러그인별 문서
```

## 라이선스

MIT License
