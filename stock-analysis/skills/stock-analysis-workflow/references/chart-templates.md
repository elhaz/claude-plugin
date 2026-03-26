# 종목분석 Plotly 차트 템플릿

종목분석 문서에 삽입하는 6종 차트 템플릿. Obsidian `plotly` 코드블록 형식.

## 1. 손익 워터폴 (LTM Financials)

매출 → 매출원가 → 매출총이익 → 판관비 → R&D → 영업이익 → 세금 → 순이익 흐름을 워터폴 차트로 표현.

````markdown
```plotly
{
  "data": [{
    "type": "waterfall",
    "orientation": "v",
    "x": ["매출", "매출원가", "매출총이익", "판관비", "R&D", "영업이익", "세금/기타", "순이익"],
    "y": [REVENUE, -COGS, null, -SGA, -RND, null, -TAX_OTHER, null],
    "measure": ["absolute", "relative", "total", "relative", "relative", "total", "relative", "total"],
    "textposition": "outside",
    "text": ["$REV", "-$COGS", "$GP", "-$SGA", "-$RND", "$OPI", "-$TAX", "$NI"],
    "connector": {"line": {"color": "rgb(63, 63, 63)"}},
    "increasing": {"marker": {"color": "#2ecc71"}},
    "decreasing": {"marker": {"color": "#e74c3c"}},
    "totals": {"marker": {"color": "#3498db"}}
  }],
  "layout": {
    "title": "손익 구조 (LTM, 단위: $M)",
    "height": 400,
    "showlegend": false
  }
}
```
````

## 2. 분기별 매출/EPS 추이 (Quarterly Trends)

매출은 막대, EPS는 라인으로 이중축 표현.

````markdown
```plotly
{
  "data": [
    {
      "x": ["Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25"],
      "y": [REV_Q4_24, REV_Q1_25, REV_Q2_25, REV_Q3_25, REV_Q4_25],
      "type": "bar",
      "name": "매출 ($M)",
      "marker": {"color": "#3498db"}
    },
    {
      "x": ["Q4'24", "Q1'25", "Q2'25", "Q3'25", "Q4'25"],
      "y": [EPS_Q4_24, EPS_Q1_25, EPS_Q2_25, EPS_Q3_25, EPS_Q4_25],
      "type": "scatter",
      "mode": "lines+markers",
      "name": "Non-GAAP EPS ($)",
      "yaxis": "y2",
      "marker": {"color": "#e74c3c"}
    }
  ],
  "layout": {
    "title": "분기별 매출 & EPS 추이",
    "height": 350,
    "yaxis": {"title": "매출 ($M)"},
    "yaxis2": {"title": "EPS ($)", "overlaying": "y", "side": "right"},
    "legend": {"x": 0, "y": 1.15, "orientation": "h"}
  }
}
```
````

## 3. 연간 매출/순이익 성장 추이 (Annual Growth)

연간 매출과 순이익을 그룹 막대로 표현.

````markdown
```plotly
{
  "data": [
    {
      "x": ["FY2022", "FY2023", "FY2024", "FY2025"],
      "y": [REV_22, REV_23, REV_24, REV_25],
      "type": "bar",
      "name": "매출 ($M)",
      "marker": {"color": "#3498db"}
    },
    {
      "x": ["FY2022", "FY2023", "FY2024", "FY2025"],
      "y": [NI_22, NI_23, NI_24, NI_25],
      "type": "bar",
      "name": "순이익 ($M)",
      "marker": {"color": "#2ecc71"}
    }
  ],
  "layout": {
    "title": "연간 매출 & 순이익 추이",
    "height": 350,
    "barmode": "group",
    "yaxis": {"title": "$M"}
  }
}
```
````

## 4. 연도별 밸류에이션 추이 (Valuation History)

P/E, EV/Revenue 등 멀티플 변화를 라인 차트로.

````markdown
```plotly
{
  "data": [
    {
      "x": ["2021", "2022", "2023", "2024", "2025"],
      "y": [PE_21, PE_22, PE_23, PE_24, PE_25],
      "type": "scatter",
      "mode": "lines+markers",
      "name": "P/E"
    },
    {
      "x": ["2021", "2022", "2023", "2024", "2025"],
      "y": [EVR_21, EVR_22, EVR_23, EVR_24, EVR_25],
      "type": "scatter",
      "mode": "lines+markers",
      "name": "EV/Revenue",
      "yaxis": "y2"
    }
  ],
  "layout": {
    "title": "연도별 밸류에이션 추이",
    "height": 350,
    "yaxis": {"title": "P/E"},
    "yaxis2": {"title": "EV/Revenue", "overlaying": "y", "side": "right"},
    "legend": {"x": 0, "y": 1.15, "orientation": "h"}
  }
}
```
````

## 5. 매출 구성 비율 (Revenue Mix)

세그먼트별 또는 지역별 매출 비율을 도넛 차트로.

````markdown
```plotly
{
  "data": [{
    "values": [SEG1_PCT, SEG2_PCT, SEG3_PCT, SEG4_PCT],
    "labels": ["세그먼트1", "세그먼트2", "세그먼트3", "세그먼트4"],
    "type": "pie",
    "hole": 0.4,
    "textinfo": "label+percent",
    "marker": {"colors": ["#3498db", "#2ecc71", "#e74c3c", "#f39c12"]}
  }],
  "layout": {
    "title": "매출 구성 (FY20XX)",
    "height": 350
  }
}
```
````

## 6. 부채/레버리지 추이 (Leverage)

부채비율과 이자보상배율의 연도별 변화.

````markdown
```plotly
{
  "data": [
    {
      "x": ["FY2022", "FY2023", "FY2024", "FY2025"],
      "y": [DEBT_EQUITY_22, DEBT_EQUITY_23, DEBT_EQUITY_24, DEBT_EQUITY_25],
      "type": "bar",
      "name": "부채비율 (D/E)",
      "marker": {"color": "#e67e22"}
    },
    {
      "x": ["FY2022", "FY2023", "FY2024", "FY2025"],
      "y": [ICR_22, ICR_23, ICR_24, ICR_25],
      "type": "scatter",
      "mode": "lines+markers",
      "name": "이자보상배율",
      "yaxis": "y2",
      "marker": {"color": "#27ae60"}
    }
  ],
  "layout": {
    "title": "부채 및 레버리지 추이",
    "height": 350,
    "yaxis": {"title": "D/E Ratio"},
    "yaxis2": {"title": "이자보상배율", "overlaying": "y", "side": "right"},
    "legend": {"x": 0, "y": 1.15, "orientation": "h"}
  }
}
```
````

## 사용법

1. 리서치 Phase에서 수집한 데이터로 위 템플릿의 플레이스홀더를 실제 값으로 치환
2. 해당 종목에 적합한 차트만 선택 (6종 모두 필수는 아님)
3. 문서 내 관련 섹션 바로 아래에 차트 삽입

### 차트 선택 기준

| 기업 유형 | 권장 차트 |
|----------|---------|
| 모든 기업 | 2(분기 추이), 3(연간 성장), 5(매출 구성) |
| 흑자 기업 | + 1(손익 워터폴), 4(밸류에이션 추이) |
| 고레버리지 | + 6(부채/레버리지) |
| 적자/프리레버뉴 | 1, 6 제외 |
