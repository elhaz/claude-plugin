# Claude Code Plugins

Claude Code용 개인 플러그인 모음입니다.

## 플러그인 목록

| 플러그인 | 설명 | 상태 |
|---------|------|------|
| [youtube-to-obsidian](./youtube-to-obsidian/) | YouTube 자막을 Obsidian 스타일 마크다운으로 변환 | ✅ 완료 |

## 설치 방법

### 1. Marketplace 등록

`~/.claude/settings.json`에 다음을 추가합니다:

```json
{
  "extraKnownMarketplaces": {
    "elhaz-plugins": {
      "source": {
        "source": "directory",
        "path": "D:/source/claude-plugin"
      }
    }
  }
}
```

> **참고**: `path`는 이 레포지토리를 clone한 로컬 경로로 변경하세요.

### 2. 플러그인 활성화

같은 `settings.json`의 `enabledPlugins`에 사용할 플러그인을 추가합니다:

```json
{
  "enabledPlugins": {
    "youtube-to-obsidian@elhaz-plugins": true
  }
}
```

### 3. Claude Code 재시작

설정 변경 후 Claude Code를 재시작하면 플러그인이 활성화됩니다.

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
