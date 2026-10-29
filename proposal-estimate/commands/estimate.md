---
name: estimate
description: 요청 요약 노트와 정한 가정으로 SI PM 페르소나 사람 견적을 뽑고 공수 산정 노트를 만든다 (절차 9~14단계)
argument-hint: "[요청 요약 노트] [PPT 경로] [PM 분야 한 줄]"
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

# 공수 산정

`proposal-estimate-workflow` 스킬을 먼저 읽고 그 절차의 9\~14단계를 진행한다.

인자: $ARGUMENTS

1. 요약 노트에서 기능 모듈 표 · 옵션 · 가정을 읽는다. 가정이 정해지지 않았으면 8단계(가정 고르기)부터 한다.
2. 9단계: PM 용 PPT 글자(금액 · 공수 줄과 고객 견적 쪽을 거른 것)와 brief 를 scratchpad 에 쓰고, 둘에 금액이 남지 않았는지 확인한 뒤 `proposal-estimate:si-pm-estimator` 를 견적 모드로 띄운다. **세션은 MD 를 직접 뽑지 않는다.**
3. 10단계: 행마다 kind 를 붙이고 `real_effort.py` 로 실작업을 계산한다.
4. 11단계: PM 모듈 검토. 사용자가 정한 가정과 부딪히는 권고는 반영 전에 묻는다.
5. 12단계: 노트 틀을 채우고 `fill_note.py` 로 숫자를 넣는다.
6. 13단계: 2차 검토가 짚은 견적 빈칸을 PM 견적 근거와 대조한다.
7. 14단계: 바뀐 판은 접힌 콜아웃 · 변경 이력으로 남긴다.

끝나면 견적 MD · 공급가(VAT 별도) · 실작업 MD · 옵션 합 · 축소안 적용 시 금액 · 일정(주)을 보고한다.
