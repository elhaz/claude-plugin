# Stock Analysis Template

Use this template structure when creating stock analysis documents.

## Document Structure

```markdown
---
tags:
  - 종목분석
  - [섹터태그]
ticker: TICK
sector: 섹터명
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# 종목명 (Company Name, TICK)

## 📊 현재 상태 (Always Current)

> [!info] 최종 업데이트: YYYY-MM-DD

### 기본 정보
- **티커**: TICK
- **현재가**: $XXX (YYYY-MM-DD)
- **시가총액**: $XXX (마이크로캡/소형주/중형주/대형주)
- **섹터**: [섹터명]
- **산업**: [산업명]
- **상장일**: YYYY-MM-DD
- **52주 최고가/최저가**: $XXX / $XXX
- **베타**: X.XX

### 투자 현황
- **평균 매수가**: $X.XX
- **현재가**: $X.XX
- **보유 수량**: XXX주
- **총 수익률**: +X.XX%

### 투자 방침 적합성

| 방침 | 적합 | 상세 평가 |
|------|------|----------|
| 1. 메가 트렌드 | ⬜/✅ | [평가] |
| 2. 대위기 매수 | ⬜/✅ | [평가] |
| 3. 변화징조 선점 | ⬜/✅ | [평가] |
| 4. 정책 수혜주 | ⬜/✅ | [평가] |
| 5. 턴어라운드 | ⬜/✅ | [평가] |
| 6. 저PER 성장주 | ⬜/✅ | [평가] |
| 7. 소외주 | ⬜/✅ | [평가] |
| 8. 탁월한 CEO | ⬜/✅ | [평가] |

---

## 📅 분기별 재무 추이

| 분기 | 매출 | 영업이익 | GAAP EPS | Non-GAAP EPS | EBITDA | 비고 |
|------|------|---------|----------|-------------|--------|------|
| YYYY Q4 | $XXX | $XXX | $X.XX | $X.XX | $XXX | [특이사항] |

### 재무 건전성

| 지표 | 값 | 비고 |
|------|---|------|
| **Current Ratio** | X.XX | |
| **FCF Yield** | X.XX% | |
| **부채비율** | XX% | |
| **현금 보유** | $XXX | |
| **해외 매출 비중** | XX% | YoY 성장률 포함 |

### 업종 특화 지표

> [!note]- 업종별 핵심 지표
> sector-metrics-guide 스킬을 참조하여 해당 업종의 핵심 지표 추가

- **핵심 지표 1**: [지표명]: [값]
- **핵심 지표 2**: [지표명]: [값]
- **GAAP vs Non-GAAP 차이**: [해당 시 설명]

### 밸류에이션 지표
- **P/E**: XX배 (업종 평균: XX배)
- **P/S**: XX배
- **PEG**: X.XX
- **EV/EBITDA**: XX배

### 적정가 산출 (YYYY-MM-DD 기준)

> [!note] 방법론 참고
> [[밸류에이션 적정가 산출 방법론]] — 기업 유형에 맞는 방법론 2~3개 교차 적용

#### 1차: [방법론명] — 핵심 산출
[계산 과정 및 결과]

#### 2차: [방법론명]
[계산 과정 및 결과]

#### 보조: Backward DCF (시장 내재 가정)
[현재 주가가 내포하는 가정 역산]

#### 적정가 종합

| 방법론 | 적정가 | 현재가 대비 |
|--------|--------|-----------|
| [1차 방법론] | $XX | +XX% |
| [2차 방법론] | $XX | +XX% |
| 애널리스트 평균 | $XX | +XX% |

**종합 적정가 범위: $XX ~ $XX** (현재가 대비 ±XX%)

> [!warning] 핵심 변수 민감도
> - [변수1 변동 시]: 적정가 $XX 변동
> - [변수2 변동 시]: 적정가 $XX 변동

### 재무 건전성
- **부채비율**: XX%
- **유동비율**: X.XX
- **이자보상배율**: XX배
- **현금**: $XXX

### 자본구조 변화
- **발행주식 변화율 (YoY)**: +X% / -X%
- **희석 원인**: ⬜ M&A / ⬜ 임직원보상 / ⬜ 유상증자 / ⬜ 해당없음
- **자사주 매입**: ⬜ 활발 / ⬜ 보통 / ⬜ 없음

---

## 🏢 사업 모델 & 경쟁력

### 핵심 가치 제안
- [고객에게 제공하는 가치]

### 수익 모델
- [수익 창출 방식]

### 경쟁 우위 (Moat Analysis)

| 우위 요소 | 평가 | 설명 |
|----------|------|------|
| 기술적 우위 | ⬜ 강함 / ⬜ 중간 / ⬜ 약함 | [설명] |
| 브랜드 파워 | ⬜ 강함 / ⬜ 중간 / ⬜ 약함 | [설명] |
| 네트워크 효과 | ⬜ 강함 / ⬜ 중간 / ⬜ 약함 | [설명] |
| 비용 우위 | ⬜ 강함 / ⬜ 중간 / ⬜ 약함 | [설명] |
| 전환 비용 | ⬜ 높음 / ⬜ 중간 / ⬜ 낮음 | [설명] |

**종합 평가**: ⬜ Wide Moat / ⬜ Narrow Moat / ⬜ No Moat

### 최근 어닝콜 핵심 Q&A

> [!note]- 어닝콜 하이라이트
> - **Bullish**: [경영진이 강조한 긍정 포인트]
> - **Bearish**: [성장 둔화, 마진 압박 등 우려 포인트]
> - **핵심 Q&A**: [애널리스트 질문 중 가장 중요한 이슈와 경영진 답변]
> - **Misses**: [경영진이 답변 회피하거나 정량화 거부한 항목]

### 업계 맥락 및 센티먼트
- **현재 섹터 센티먼트**: ⬜ 강세 / ⬜ 중립 / ⬜ 약세
- **센티먼트 원인**: [설명]
- **최근 업계 주요 이슈**: [설명]

### 경쟁사 분석

| 경쟁사 | 시총 | 특징 | 비교 우위/열위 |
|--------|------|------|---------------|
| 경쟁사1 | $XXX | [특징] | [평가] |

---

## 👨‍💼 CEO 정보

### 기본 정보
- **이름**: [CEO 이름]
- **재임 기간**: YYYY년~ (X년 재임)
- **주요 경력**: [핵심 경력]

### 투자 방침 8번 적합성 (탁월한 CEO)

**평가**: ⬜ 충족 / ⬜ 미충족

**근거**:
- [ ] 업계 10년 이상 경력
- [ ] 혁신적 비전 제시
- [ ] 주주가치 증대 실적
- [ ] Skin in the Game

---

## 📋 SWOT 분석

| | 긍정 | 부정 |
|---|------|------|
| **내부** | **Strengths**: | **Weaknesses**: |
| | - [강점 1] | - [약점 1] |
| | - [강점 2] | - [약점 2] |
| **외부** | **Opportunities**: | **Threats**: |
| | - [기회 1] | - [위협 1] |
| | - [기회 2] | - [위협 2] |

---

## 🔔 리스크 요인

| 리스크 유형 | 수준 | 설명 |
|------------|------|------|
| 사업 모델 리스크 | ⬜ 높음 / ⬜ 중간 / ⬜ 낮음 | [설명] |
| 경쟁 리스크 | ⬜ 높음 / ⬜ 중간 / ⬜ 낮음 | [설명] |
| 재무 리스크 | ⬜ 높음 / ⬜ 중간 / ⬜ 낮음 | [설명] |
| 규제 리스크 | ⬜ 높음 / ⬜ 중간 / ⬜ 낮음 | [설명] |

### 리스크 모니터링 지표
- **추적 지표 1**: [지표명 및 기준]
- **경고 신호**: [손절 고려 시점]

---

## 📝 다음 액션

- [ ] [액션 1]
- [ ] [액션 2]

---

**태그**: #종목분석 #[섹터] #[티커]
```

## Key Sections Explained

### 업종 특화 지표

This section is critical for accurate valuation. Different industries use different key metrics:

- **Asset Managers**: FRE, DE, Permanent Capital %
- **REITs**: FFO, AFFO, Cap Rate
- **SaaS**: ARR, NRR, Rule of 40
- **Banks**: NIM, CET1, Efficiency Ratio

Always consult `sector-metrics-guide` for the relevant metrics.

### 자본구조 변화

Track share dilution carefully:
- High dilution (>10%/year) erodes per-share value
- Look for causes: M&A, stock compensation, capital raises
- Note buyback activity as a positive signal

### 업계 맥락 및 센티먼트

Context matters for timing:
- Why is the sector weak/strong?
- What recent events affect sentiment?
- Is the company leading or lagging peers?

### CEO 평가

Management quality indicators:
- Track record at previous companies
- Insider buying (especially cluster buys)
- Alignment of incentives with shareholders
- Communication clarity in earnings calls
