# Claude Code Plugins

[Claude Code](https://claude.com/claude-code)용 개인 플러그인 모음 (마켓플레이스: `elhaz-plugins`).

## 플러그인 목록

| 플러그인 | 버전 | 설명 | 구성 |
|---------|------|------|------|
| [youtube-to-obsidian](./youtube-to-obsidian/) | 1.2.0 | YouTube 자막을 Obsidian 스타일 마크다운으로 변환, 핵심 장면 이미지 추출 | commands, skills, scripts |
| [stock-analysis](./stock-analysis/) | 2.2.0 | 주식 종목분석 자동화 (2-Agent 파이프라인 Sonnet+Opus, 다국가, 밸류에이션, Plotly 차트) | commands, skills, agents |
| [macro-report](./macro-report/) | 1.5.1 | 거시경제 종합 투자분석 보고서 (5개 개별 분석 + 종합 투자판단 + 추천 종목 백테스트, fdp capabilities 우선 + data_gaps 짝꿍) | commands, skills, agents |
| [dailylog](./dailylog/) | 0.2.0 | Obsidian 데일리로그 관리 (날짜별 읽기, 항목 추가, 통계 요약) | commands, skills, scripts |
| [nanobanana](./nanobanana/) | 2.0.0 | Gemini AI 이미지 생성/편집 (Nano Banana 2 / Pro) | commands, skills |
| [openai-image](./openai-image/) | 1.3.0 | OpenAI 이미지 생성/편집 (hq=gpt-image-1.5 인증불필요 / fast=gpt-image-1-mini / v2=gpt-image-2 인증필요, 마스크 편집, 투명 배경, prompt-rewriter 에이전트, 기본 webp) | commands, skills, agents |

마켓플레이스 메타데이터: `.claude-plugin/marketplace.json` (현재 v1.9.1)

## 설치 방법

### 1. 마켓플레이스 등록

Claude Code에서 다음 명령어를 실행:

```
/plugin marketplace add elhaz/claude-plugin
```

### 2. 플러그인 활성화

```
/plugin install <플러그인명>@elhaz-plugins
```

또는 `/plugin` 대화형 메뉴에서 선택.

### 3. 변경사항 반영

source 레포에서 수정한 후 즉시 반영하려면:

```
/reload-plugins
```

## 저장소 구조

멀티 플러그인 모노레포 구조:

```
claude-plugin/                            # 저장소 루트
├── .claude-plugin/
│   └── marketplace.json                  # 마켓플레이스 메타데이터 (모든 플러그인 버전 등록)
├── youtube-to-obsidian/                  # 개별 플러그인 1
│   ├── .claude-plugin/
│   │   └── plugin.json                   # 플러그인 매니페스트
│   ├── skills/
│   │   └── youtube-obsidian/
│   │       ├── SKILL.md                  # 스킬 정의 (frontmatter에 version)
│   │       └── references/               # 참조 문서
│   ├── commands/                         # 슬래시 커맨드 (.md)
│   └── scripts/                          # 헬퍼 스크립트
├── stock-analysis/                       # 개별 플러그인 2
│   ├── .claude-plugin/plugin.json
│   ├── agents/                           # 서브에이전트 정의
│   ├── commands/
│   └── skills/
├── macro-report/                         # 개별 플러그인 3
│   ├── .claude-plugin/plugin.json
│   ├── agents/
│   ├── commands/
│   └── skills/
├── dailylog/                             # 개별 플러그인 4
├── nanobanana/                           # 개별 플러그인 5
├── openai-image/                         # 개별 플러그인 6
│   ├── .claude-plugin/plugin.json
│   ├── agents/                           # prompt-rewriter 서브에이전트
│   ├── commands/
│   └── skills/
└── README.md
```

## 기여 / 수정 지침

### 스킬·커맨드를 생성/수정할 때 — 버전 갱신 필수

스킬, 커맨드, 에이전트를 **새로 만들거나 기존 것을 수정**한 경우 다음 **3개 파일의 버전을 반드시 함께 업데이트**해야 합니다 (semver 준수):

1. **`<plugin>/.claude-plugin/plugin.json`** — 해당 플러그인 매니페스트의 `version` 필드
2. **`.claude-plugin/marketplace.json`** — 두 군데 모두 갱신
   - `plugins[].version` (해당 플러그인 항목)
   - `metadata.version` (마켓플레이스 전체 버전)
3. **`<plugin>/skills/<skill>/SKILL.md`** — 영향받은 스킬의 frontmatter `version`

#### Semver 가이드

| 변경 종류 | 버전 증분 | 예시 |
|---|---|---|
| 버그 수정·오타·작은 문구 보정 | **patch** (x.y.**z**) | 1.2.0 → 1.2.1 |
| 기능 추가·옵션 추가·기존 동작 호환 유지하는 개선 | **minor** (x.**y**.0) | 1.2.0 → 1.3.0 |
| 인자 시그니처 변경·동작 방식 호환성 깨짐 | **major** (**x**.0.0) | 1.2.0 → 2.0.0 |

> 마켓플레이스 메타데이터(`metadata.version`)는 어떤 플러그인이든 변경되면 함께 bump.

#### 예시 워크플로우

`macro-report` 플러그인의 `commands/backtest.md`에 새 옵션을 추가했다면:

```text
1. macro-report/.claude-plugin/plugin.json          : version 1.2.0 → 1.3.0
2. .claude-plugin/marketplace.json
   - plugins[macro-report].version                  : 1.2.0 → 1.3.0
   - metadata.version                               : 1.2.0 → 1.3.0
3. macro-report/skills/macro-report-workflow/SKILL.md : version 1.1.0 → 1.2.0 (해당 스킬이 영향받는 경우)
```

### 일반 작성 규칙

- 커밋 메시지·코드 주석은 한국어로
- 이모지는 코드/매니페스트에 넣지 않음
- 새 스킬은 반드시 `description` frontmatter를 명확히 — Claude가 스킬을 찾는 핵심 신호
- 커맨드 파일(`commands/*.md`)의 frontmatter `allowed-tools`에 사용하는 모든 도구 등록
- 변경 후에는 `/reload-plugins`로 동작 검증

## 라이선스

MIT License
