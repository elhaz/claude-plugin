# proposal-estimate

고객 제안서(PPT)를 받아 Obsidian 볼트에 두 노트를 만드는 플러그인이다.

- **요청 요약 노트**: 쪽 번호 근거, 받는 쪽별 질문, 표기 · 용어, 기능 모듈 표, 전문가 검토, 레인 그림
- **공수 산정 노트(내부용)**: 견적(AI 없이 사람) · 실작업(AI 사용) 두 열, 금액, 옵션, 늘어나는 요인, 1차 오픈 축소안, 하자보수

견적은 세션이 아니라 **SI PM 페르소나 서브에이전트**가 뽑는다. 페르소나에게는 금액 · 공수 줄을 거른 PPT 글자와 견적 입력만 준다. 세션은 앞선 금액을 이미 본 상태라 그 숫자에 끌리기 때문이다. 실작업은 그 견적에 일 종류별 배율을 곱해 계산한다.

## 설치

```
/plugin marketplace add elhaz/claude-plugin
/plugin install proposal-estimate@elhaz-plugins
```

필요한 것: `uv`(스크립트 실행), 레인 그림 PNG 를 뽑으려면 `diagram-design` 플러그인 또는 볼트의 래스터 스크립트.
PPT 추출은 `uv run --with python-pptx` 로 그때그때 받는다.

## 사용

```
/proposal-estimate:summarize "D:\자료\제안서.pptx" "01_Projects/회사업무/고객사" "철골 제작사 출하 · 설치 실무 책임자" "D:\source\기존코드"
/proposal-estimate:estimate "01_Projects/회사업무/고객사/2026-10-23 과제 요청 내용 요약.md" "D:\자료\제안서.pptx" "철골 · 중공업 고객 웹 시스템 SI PM"
```

- `summarize` 는 절차 1\~8단계(요약 노트, 전문가 검토 1 · 2차, 레인 그림, 가정 고르기)를 한다. 새 모듈이면 기존 코드 경로를 빼면 아키텍처 검토를 건너뛴다.
- `estimate` 는 9\~14단계(PM 견적, 실작업 계산, PM 모듈 검토, 노트 채우기, 빈칸 대조, 옛 판 접기)를 한다.
- 명령 없이 「제안서 정리해 줘」 · 「공수 산정해 줘」 라고 해도 스킬 `proposal-estimate-workflow` 가 같은 절차를 안내한다.

## 구성

| 종류 | 이름 | 하는 일 |
|---|---|---|
| 스킬 | `proposal-estimate-workflow` | 14단계 절차, 노트 규칙 · 틀 |
| 명령 | `summarize`, `estimate` | 절차 앞 · 뒤 절반 |
| 에이전트 | `si-pm-estimator` | SI PM 페르소나. 견적 · 모듈 검토 · 부분 재산정 |
| 에이전트 | `domain-practitioner` | 도메인 실무 페르소나(역할을 인자로). 1 · 2차 검토 |
| 에이전트 | `code-architect-reviewer` | 기존 코드 아키텍처 검토(대상 코드 경로를 인자로) |
| 스크립트 | `ppt_extract.py` | PPT 글자 추출, 쪽 범위 · 금액 줄 · 공수 줄 거르기 |
| 스크립트 | `real_effort.py` | 견적 × 일 종류별 배율 = 실작업, 0.5 MD 반올림, 금액 |
| 스크립트 | `fill_note.py` | 공수 산정 노트 틀 채우기(옵션 · 축소안 · 일정 자동 계산) |
| 스크립트 | `lane_diagram.py` | 레인 그림 틀(JSON 명세 → diagram-design HTML) |

## 설정

기본값은 [config/settings.json](config/settings.json) 이다. 바꿀 키만 `~/.claude/proposal-estimate.json`(또는 환경변수 `PROPOSAL_ESTIMATE_CONFIG` 가 가리키는 파일)에 적는다.

| 키 | 기본값 | 뜻 |
|---|---|---|
| `rate.daily_won` | 378,250 | 2026 응용SW개발자 일평균임금 (SW기술자 평균임금 공표) |
| `rate.monthly_won` | 7,754,124 | 같은 자료의 월평균임금 |
| `rate.workdays_per_month` | 20.5 | M/M 환산 근무일 |
| `rate.source_file` | 공표 PDF 경로 | 노트 4.1 절 「원문」 칸 |
| `factors.dev` | 0.45 | 화면 · 기능 개발 · 문서 |
| `factors.logic` | 0.6 | 계산 로직 · 기존 코드 수정 · 서버 · 데이터 이관 · 테스트 |
| `factors.analysis` | 0.75 | 분석 · 설계 · 명세 · 검수 시나리오 |
| `factors.meeting` | 1.0 | 회의 · 교육 |
| `rounding_md` | 0.5 | 실작업 반올림 단위 |
| `schedule.md_per_week` | 5 | 일정(주) 계산 |
| `notes.default_dir` | `01_Projects/회사업무` | 노트 폴더를 안 줬을 때 찾는 곳(`OBSIDIAN_VAULT` 기준) |

예: 해가 바뀌어 단가가 바뀌면

```json
{ "rate": { "daily_won": 390000, "monthly_won": 7995000, "applies": "2027-01-01 ~ 2027-12-31", "source_file": "D:\\자료\\2027 공표.pdf" } }
```

배율은 가정이다. 실제 작업 기록이 쌓이면 고친다.

## 스크립트 단독 사용

```bash
P=~/.claude/plugins/cache/elhaz-plugins/proposal-estimate/0.1.0
uv run --with python-pptx python $P/scripts/ppt_extract.py 제안서.pptx -o pm.txt --exclude 38 --drop-money --drop-effort
uv run python $P/scripts/real_effort.py pm_estimate.json -o result.json
uv run python $P/scripts/fill_note.py 노트초안.md pm_estimate.json result.json -o 노트.md
uv run python $P/scripts/lane_diagram.py lane_spec.json -o 그림.dd.html
```

형식 예: [examples/pm_estimate_example.json](examples/pm_estimate_example.json), [examples/lane_spec_example.json](examples/lane_spec_example.json).

## 시험

```bash
uv run python -m unittest discover -s proposal-estimate/tests
```

## 버전

- 0.1.0: 첫 판. 두 사례(새 모듈 · 기존 코드 고도화)로 다듬은 절차를 옮겼다.
