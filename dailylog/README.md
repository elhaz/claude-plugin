# dailylog

Obsidian 데일리로그 관리를 위한 Claude Code 플러그인

## 개요

연도별 단일 파일로 관리되는 Obsidian 데일리로그를 효율적으로 읽고, 수정하고, 요약하는 도구를 제공합니다.

## 기능

- **읽기 (read)**: 날짜별, 기간별 데일리로그 조회
- **추가 (add)**: 특정 섹션에 항목 추가 (날짜 없으면 자동 생성)
- **요약 (summary)**: 통계 기반 기간 요약 + AI 자연어 요약

## 설치

```bash
# Claude Code 플러그인으로 설치
claude --plugin-dir /path/to/dailylog
```

## 사용법

### 읽기

```bash
/dailylog read              # 오늘
/dailylog read yesterday    # 어제
/dailylog read 2026-01-15   # 특정 날짜
/dailylog read --week       # 이번 주
/dailylog read --month      # 이번 달
```

### 추가

```bash
/dailylog add --section 회사 "팀 미팅 참석"
/dailylog add --section 개인 --date yesterday "운동 1시간"
```

### 요약

```bash
/dailylog summary --week    # 이번 주 통계
/dailylog summary --month   # 이번 달 통계
```

## 데일리로그 구조

```
02_Areas/일지/데일리로그 2026.md
├── ## 1월
│   ├── ### 1월 2주차 (01/05 - 01/09)
│   │   ├── #### 2026-01-08 (목)
│   │   │   ├── ##### 회사
│   │   │   ├── ##### 개인
│   │   │   ├── ##### 스크랩
│   │   │   └── ##### 아이디어
│   │   └── ...
│   └── ...
└── ...
```

## 섹션

| 섹션 | 용도 |
|------|------|
| 회사 | 업무 관련 기록 |
| 개인 | 개인 생활, 취미 |
| 스크랩 | 읽은 글, 저장한 링크 |
| 아이디어 | 떠오른 생각, 메모 |

## 요구사항

- Python 3.10+
- uv (Python 패키지 매니저)
- Obsidian Vault 루트에서 실행

## 컴포넌트

```
dailylog/
├── .claude-plugin/
│   └── plugin.json         # 플러그인 매니페스트
├── commands/
│   └── dailylog.md         # /dailylog 커맨드
├── scripts/
│   └── dailylog.py         # 핵심 파싱/수정 로직
├── skills/
│   └── dailylog-guide/
│       └── SKILL.md        # 데일리로그 사용 가이드
└── README.md
```

## 라이선스

MIT
