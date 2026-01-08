---
name: dailylog
description: Obsidian 데일리로그 읽기, 항목 추가, 요약 기능
argument-hint: <action> [options] - read, add, summary
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# 데일리로그 관리 커맨드

Obsidian Vault의 데일리로그 파일을 관리한다. 현재 작업 디렉토리가 Vault 루트라고 가정한다.

## 사용 방법

### 1. 읽기 (read)

```
/dailylog read [날짜] [옵션]
```

**날짜 형식:**
- `today` (기본값) - 오늘
- `yesterday` - 어제
- `2026-01-15` - 특정 날짜
- `01-15` - 현재 연도의 특정 날짜

**옵션:**
- `--week` - 이번 주 전체
- `--month` - 이번 달 전체
- `--from YYYY-MM-DD --to YYYY-MM-DD` - 기간 지정

### 2. 추가 (add)

```
/dailylog add --section <섹션> "내용"
/dailylog add --section <섹션> --date <날짜> "내용"
```

**섹션:** 회사, 개인, 스크랩, 아이디어

### 3. 요약 (summary)

```
/dailylog summary [옵션]
```

**옵션:**
- `--week` - 이번 주 (기본값)
- `--month` - 이번 달
- `--from YYYY-MM-DD --to YYYY-MM-DD` - 기간 지정

## 실행 방법

Python 스크립트를 통해 실행한다:

```bash
SCRIPT_PATH="${CLAUDE_PLUGIN_ROOT}/scripts/dailylog.py"
PYTHONIOENCODING=utf-8 uv run "$SCRIPT_PATH" <action> [options]
```

## 처리 워크플로우

### read 요청 시

1. 인자에서 날짜/옵션 파싱
2. Python 스크립트 실행:
   ```bash
   PYTHONIOENCODING=utf-8 uv run "${CLAUDE_PLUGIN_ROOT}/scripts/dailylog.py" read <date> [--week|--month|--from X --to Y]
   ```
3. 결과 출력

### add 요청 시

1. 인자에서 섹션, 날짜, 내용 파싱
2. Python 스크립트 실행:
   ```bash
   PYTHONIOENCODING=utf-8 uv run "${CLAUDE_PLUGIN_ROOT}/scripts/dailylog.py" add --section <섹션> [--date <날짜>] "<내용>"
   ```
3. 결과 확인 및 안내

### summary 요청 시

1. 인자에서 옵션 파싱
2. Python 스크립트로 통계 요약 생성:
   ```bash
   PYTHONIOENCODING=utf-8 uv run "${CLAUDE_PLUGIN_ROOT}/scripts/dailylog.py" summary [--week|--month|--from X --to Y]
   ```
3. 통계 결과 출력
4. **AI 요약 추가**: 사용자가 원하면 통계 결과를 바탕으로 자연어 요약 제공

## 예시

```
# 오늘 데일리로그 읽기
/dailylog read

# 어제 읽기
/dailylog read yesterday

# 이번 주 읽기
/dailylog read --week

# 회사 섹션에 항목 추가
/dailylog add --section 회사 "팀 미팅 참석"

# 어제 개인 섹션에 추가
/dailylog add --section 개인 --date yesterday "운동 1시간"

# 이번 달 요약
/dailylog summary --month
```

## 오류 처리

- 데일리로그 파일이 없는 경우: 파일 경로와 함께 안내
- 날짜 형식 오류: 지원 형식 안내
- 섹션 오류: 유효한 섹션 목록 안내

## 중요 사항

1. **Vault 경로**: 현재 작업 디렉토리가 Obsidian Vault 루트여야 한다
2. **파일 경로**: `02_Areas/일지/데일리로그 {year}.md` 패턴 사용
3. **인코딩**: `PYTHONIOENCODING=utf-8` 필수 (한글 처리)
4. **자동 생성**: add 시 해당 날짜 섹션이 없으면 템플릿 기반 자동 생성
