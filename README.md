# Claude Code Plugins

Claude Code용 개인 플러그인 모음입니다.

## 플러그인 목록

| 플러그인 | 설명 | 상태 |
|---------|------|------|
| [youtube-to-obsidian](./youtube-to-obsidian/) | YouTube 자막을 Obsidian 스타일 마크다운으로 변환 | ✅ 완료 |

## 설치 방법

### 1. Marketplace 등록

Claude Code에서 다음 명령어를 실행합니다:

```
/plugin elhaz/claude-plugin
```

### 2. 플러그인 활성화

설치 프롬프트에서 원하는 플러그인을 선택하여 활성화합니다.

## 플러그인 구조

멀티 플러그인 저장소 구조:

```
claude-plugin/                          # 저장소 루트
├── .claude-plugin/
│   └── marketplace.json                # 마켓플레이스 메타데이터
├── youtube-to-obsidian/                # 개별 플러그인
│   ├── .claude-plugin/
│   │   └── plugin.json                 # 플러그인 매니페스트
│   ├── skills/
│   │   └── youtube-obsidian/
│   │       ├── SKILL.md                # 스킬 정의
│   │       └── references/             # 참조 문서
│   ├── commands/                       # 슬래시 커맨드
│   └── scripts/                        # 헬퍼 스크립트
└── README.md
```

## 라이선스

MIT License
