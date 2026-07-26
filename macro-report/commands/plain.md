---
name: plain
description: 이미 작성된 보고서의 쉬운말 버전을 생성합니다 (전문 용어를 풀어쓴 평이판)
argument-hint: "[type|all] [date] [output-path]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
---

# /macro-report:plain

이미 작성된 보고서를 읽어 **쉬운말 버전**만 생성한다. 웹 검색이나 데이터 수집 없이 기존 보고서만 활용하므로 빠르고 저렴하다.

`/macro-report:generate` 는 Step 4에서 이 작업을 자동 수행한다. 이 커맨드는 다음 경우에 쓴다:

- 과거 보고서에 소급 적용할 때
- `--no-plain` 으로 생성했다가 나중에 필요해졌을 때
- generate 중 일부 쉬운말 생성이 실패해 재생성할 때
- 원본을 수정한 뒤 쉬운말 버전을 갱신할 때

## Arguments

- **type** (선택): `insider` | `analyst` | `sector` | `liquidity` | `regime` | `comprehensive` | `all`. 기본값: `all`
- **date** (선택): 대상 보고서 날짜 (YYYY-MM-DD). 기본값: 오늘
- **output-path** (선택): 보고서 디렉토리. 기본값: `02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/`

### type 매핑

| type | 원본 파일명 | 생성될 파일명 |
|------|-----------|-------------|
| `insider` | `[date] 내부자 매매 동향.md` | `[date] 내부자 매매 동향 쉬운 설명.md` |
| `analyst` | `[date] 애널리스트 목표가 변동.md` | `[date] 애널리스트 목표가 변동 쉬운 설명.md` |
| `sector` | `[date] 시장 주도 업종 분석.md` | `[date] 시장 주도 업종 분석 쉬운 설명.md` |
| `liquidity` | `[date] 유동성 환경 분석.md` | `[date] 유동성 환경 분석 쉬운 설명.md` |
| `regime` | `[date] 크로스에셋 레짐 분석.md` | `[date] 크로스에셋 레짐 분석 쉬운 설명.md` |
| `comprehensive` | `[date] 종합 분석 및 투자 판단.md` | `[date] 종합 분석 쉬운 설명.md` |
| `all` | 위 6개 전부 | 위 6개 전부 (병렬 생성) |

## 실행 순서

### Step 0: 원본 보고서 탐색

지정된 `type` 과 `date` 로 원본을 Glob 탐색한다.

- `type=all` 이면 6개를 모두 찾는다. 일부가 없으면 **있는 것만 처리**하고 없는 목록을 완료 보고에 명시한다 (중단하지 않음)
- `type` 이 개별 지정이면 해당 1개만 찾는다. 없으면 사용자에게 알리고 종료
- **덮어쓰기 확인**: 생성될 쉬운말 파일이 이미 존재하면 사용자에게 알리고 진행 여부를 확인한다

### Step 1: 쉬운말 버전 작성 (macro-writer × N, 병렬)

```
Agent(macro-writer) × N 병렬:
  각각에 전달:
  - mode: plain
  - report_type: [type]
  - source_report_path: Step 0에서 확인된 원본 경로
  - plain_guide_path: references/plain-language-guide.md 경로
  - output_path: [output-path]/[date] [보고서명] 쉬운 설명.md
  - report_date: [date]
```

> [!important] 병렬 실행 + 경로만 전달
> `type=all` 이면 6개 에이전트를 **하나의 메시지에서 동시에** 호출한다. 각 에이전트는 자기 원본 1개만 Read하므로 서로 간섭하지 않는다.
> 작성 규칙의 단일 출처는 `references/plain-language-guide.md` 이며, 오케스트레이터는 이 파일을 읽지 않고 **경로만 전달**한다.

각 에이전트는 쉬운말 문서를 Write한 뒤, 원본의 `## 관련문서` 맨 위에 역링크 1줄을 Edit로 삽입한다.

### Step 2: 완료 보고

생성된 파일 경로와 각 문서의 핵심 요약 1줄을 보고한다. 원본이 없어 건너뛴 항목, 실패한 항목이 있으면 함께 명시한다.

## 에러 처리

- 개별 실패는 나머지 생성을 막지 않는다
- 원본이 없으면 그 항목만 건너뛴다 (`type=all` 인 경우)
- **원본은 어떤 경우에도 내용이 변경되지 않는다** — `## 관련문서` 에 역링크 1줄을 추가하는 것이 원본에 대한 유일한 쓰기 작업이다

## 사용 예시

```
/macro-report:plain
/macro-report:plain comprehensive
/macro-report:plain all 2026-07-26
/macro-report:plain liquidity 2026-07-19
/macro-report:plain all 2026-07-26 02_Areas/생활/재정관리/투자전략/투자 계획/AI 리포트/분석/
```
