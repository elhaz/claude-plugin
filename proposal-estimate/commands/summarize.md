---
name: summarize
description: 고객 제안서(PPT)에서 요청 요약 노트를 만든다 (절차 1~8단계)
argument-hint: "[PPT 경로] [노트 폴더] [고객 실무 역할] [기존 코드 경로(선택)]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - PowerShell
  - Agent
  - AskUserQuestion
  - Skill
---

# 제안서 요청 요약

`proposal-estimate-workflow` 스킬을 먼저 읽고 그 절차의 1\~8단계를 진행한다.

인자: $ARGUMENTS

1. 인자에서 PPT 경로, 노트를 둘 볼트 폴더, 도메인 실무 페르소나의 역할, 기존 코드 경로(있으면)를 읽는다. 빠진 것은 한 번에 묻는다.
   - 노트 폴더를 안 주면 설정 `notes.default_dir` 아래에서 고객 폴더를 찾아 제안한다.
   - 기존 코드 경로가 없으면 새 모듈로 보고 아키텍처 검토를 건너뛴다.
2. 1단계: PPT 글자를 scratchpad 에 뽑고 「원본」 절을 쓴다.
3. 2\~4단계: 표기 · 용어 · 요청 내용 · 기능 모듈 표 · 질문(받는 쪽별)으로 요약 노트를 만든다. 틀은 `references/summary-note-template.md`.
4. 5단계: 전문가 검토를 동시에 띄우고, PPT 원문으로 대조해 반영한다. 원문은 「검토 원문」 노트로.
5. 6단계: 레인 그림을 만들고 PNG 를 열어 확인한 뒤 노트에 넣는다.
6. 7단계: 2차 검토. 견적 빈칸 목록을 남긴다.
7. 8단계: 답 없는 질문의 가정을 사용자에게 고르게 한다(추천 = A).

끝나면 만든 노트 경로, 기능 모듈 수, 질문 수(받는 쪽별), 정한 가정 수를 보고하고 `/proposal-estimate:estimate` 로 이어 갈지 묻는다.
