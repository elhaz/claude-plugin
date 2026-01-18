# Research Plugin

체계적인 심층 연구 워크플로우를 제공하는 Claude Code 플러그인입니다.

## 원본 출처

이 플러그인은 [Weizhena/Deep-Research-skills](https://github.com/Weizhena/Deep-Research-skills)를 기반으로 포크 및 수정되었습니다.

## 워크플로우

```
/research <topic>     예비 조사: outline.yaml + fields.yaml 생성
        ↓
/research-add-items   (선택) 연구 항목 추가
/research-add-fields  (선택) 필드 정의 추가
        ↓
/research-deep        심층 조사: 병렬 에이전트로 각 항목 조사
        ↓
/research-report      보고서 생성: JSON → Markdown 변환
```

## 명령어

| 명령어 | 설명 |
|--------|------|
| `/research <topic>` | 예비 조사 시작, 연구 프레임워크 생성 |
| `/research-add-items` | 연구 항목(objects) 추가 |
| `/research-add-fields` | 필드 정의 추가 |
| `/research-deep` | 병렬 에이전트로 심층 조사 실행 |
| `/research-report` | JSON 결과를 마크다운 보고서로 변환 |

## 출력 구조

```
{topic_slug}/
├── outline.yaml              # 연구 항목 목록 + 실행 설정
├── fields.yaml               # 필드 정의 (required/fallback 지원)
├── web_search_supplement.md  # 웹 검색 보충 결과 (Step 2)
├── progress.json             # 진행 상황 추적
├── results/                  # 항목별 JSON 결과
│   ├── item1.json
│   ├── item2.json
│   └── ...
├── generate_report.py        # 보고서 생성 스크립트
└── report.md                 # 최종 보고서
```

## 주요 기능

### 필드 정의 개선
- `required`: 필수/선택 필드 구분
- `fallback`: 기본값 설정 (선택 필드용)
- 소스 추적: `_source`, `_retrieved_at` 메타데이터

### 실행 설정
- `items_per_agent`: 에이전트당 항목 수 (기본값: 2, 타임아웃 방지)
- `batch_size`: 병렬 에이전트 수 (기본값: 3)
- `progress_file`: 진행 상황 추적 파일

### 한글 지원
- 한글 토픽/파일명 그대로 유지
- 공백만 언더스코어로 변환

## 스크립트

- `scripts/validate_json.py` - JSON 결과 필드 커버리지 검증

## 활용 사례

- 기술 조사 (AI Coding Tools, LLM 비교, 프레임워크 선택 등)
- 벤치마크 연구
- 학술 연구 (논문 리뷰, 연구 동향 분석)
- 시장 조사
- 경쟁사 분석

## 라이선스

원본 프로젝트의 라이선스를 따릅니다.
