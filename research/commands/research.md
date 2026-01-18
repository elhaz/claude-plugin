---
user-invocable: true
allowed-tools: Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: Conduct preliminary research on a topic and generate research outline. For academic research, benchmark research, technology selection, etc.
---

# Research Skill - Preliminary Research

## Trigger
`/research <topic>`

## Workflow

### Step 1: Generate Initial Framework from Model Knowledge
Based on topic, use model's existing knowledge to generate:
- Main research objects/items list in this domain
- Suggested research field framework

Output {step1_output}, use AskUserQuestion to confirm:
- Need to add/remove items?
- Does field framework meet requirements?

### Step 2: Web Search Supplement
Use AskUserQuestion to ask for time range (e.g., last 6 months, since 2024, unlimited).

**Pre-requisite**: Create output directory `./{topic_slug}/` BEFORE launching web-search-agent.
- 한글 파일명 지원: 한글 토픽은 그대로 유지 (예: "AI_코딩_도구" O, "ai_coding_tools" X)
- 공백만 언더스코어로 변환, 특수문자 제거

**Parameter Retrieval**:
- `{topic}`: User input research topic
- `{YYYY-MM-DD}`: Current date
- `{step1_output}`: Complete output from Step 1
- `{time_range}`: User specified time range
- `{output_path}`: Absolute path to `{topic_slug}/web_search_supplement.md`

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

Launch 1 web-search-agent (background), **Prompt Template**:
```python
prompt = f"""## Task
Research topic: {topic}
Current date: {YYYY-MM-DD}

Based on the following initial framework, supplement latest items and recommended research fields.

## Existing Framework
{step1_output}

## Goals
1. Verify if existing items are missing important objects
2. Supplement items based on missing objects
3. Continue searching for {topic} related items within {time_range} and supplement
4. Supplement new fields

## Output Requirements
Write results to {output_path} (MUST save file, not just return content):

### Supplementary Items
- item_name: Brief explanation (why it should be added)
...

### Recommended Supplementary Fields
- field_name: Field description (why this dimension is needed)
...

### Sources
- [Source1](url1)
- [Source2](url2)
"""
```

**One-shot Example** (assuming researching AI Coding History):
```
## Task
Research topic: AI Coding History
Current date: 2025-12-30

Based on the following initial framework, supplement latest items and recommended research fields.

## Existing Framework
### Items List
1. GitHub Copilot: Developed by Microsoft/GitHub, first mainstream AI coding assistant
2. Cursor: AI-first IDE, based on VSCode
...

### Field Framework
- Basic Info: name, release_date, company
- Technical Features: underlying_model, context_window
...

## Goals
1. Verify if existing items are missing important objects
2. Supplement items based on missing objects
3. Continue searching for AI Coding History related items within since 2024 and supplement
4. Supplement new fields

## Output Requirements
Write results to /path/to/AI_Coding_History/web_search_supplement.md (MUST save file, not just return content):

### Supplementary Items
- item_name: Brief explanation (why it should be added)
...

### Recommended Supplementary Fields
- field_name: Field description (why this dimension is needed)
...

### Sources
- [Source1](url1)
- [Source2](url2)
```

### Step 3: Ask User for Existing Fields
Use AskUserQuestion to ask if user has existing field definition file, if so read and merge.

### Step 4: Generate Outline (Separate Files)
**Pre-requisite**: Wait for web-search-agent to complete, then read `{topic_slug}/web_search_supplement.md` to get {step2_output}.

Merge {step1_output}, {step2_output} and user's existing fields, generate two files:

**outline.yaml** (items + config):
- topic: Research topic
- items: Research objects list
- execution:
  - batch_size: Number of parallel agents (default: 3, confirm with AskUserQuestion)
  - items_per_agent: Items per agent (default: 2, recommend 2 to prevent timeout, confirm with AskUserQuestion)
  - output_dir: Results output directory (default: ./results)
  - progress_file: Progress tracking file (default: ./progress.json)

**fields.yaml** (field definitions):
- Field categories and definitions
- Each field's name, description, detail_level, required, fallback
  - required: true/false (필수 필드 여부)
  - fallback: null 또는 기본값 (필수 필드는 null, 선택 필드는 "[uncertain]")
- detail_level hierarchy: brief -> moderate -> detailed
- uncertain: Uncertain fields list (reserved field, auto-filled in deep phase)

**필수 필드 권장 목록** (연구 주제에 따라 적절히 선택):
- identifier/name (식별자)
- title/full_name (정식 명칭)
- category/type (분류)
- date/release_date (관련 날짜)
- description/summary (개요)
- source_url (출처)

### Step 5: Output and Confirm
- Directory `./{topic_slug}/` was already created in Step 2
- Save: `outline.yaml` and `fields.yaml` to the same directory
- Show to user for confirmation

## Output Path
```
{current_working_directory}/{topic_slug}/
  ├── outline.yaml              # items list + execution config
  ├── fields.yaml               # field definitions
  └── web_search_supplement.md  # web search results (Step 2)
```

## Follow-up Commands
- `/research-add-items` - Supplement items
- `/research-add-fields` - Supplement fields
- `/research-deep` - Start deep research
