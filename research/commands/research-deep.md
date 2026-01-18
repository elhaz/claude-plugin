---
user-invocable: true
description: Read research outline, launch independent agent for each item for deep research. Disable task output.
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task
---

# Research Deep - Deep Research

## Trigger
`/research-deep`

## Workflow

### Step 1: Auto-locate Outline
Find `*/outline.yaml` file in current working directory, read items list, execution config (including items_per_agent).

### Step 2: Resume Check
- Check completed JSON files in output_dir
- Skip completed items

### Step 3: Batch Execution
- Batch by batch_size (need user approval before next batch)
- Each agent handles items_per_agent items
- Launch web-search-agent (background parallel, disable task output)

**Parameter Retrieval**:
- `{topic}`: topic field from outline.yaml
- `{item_name}`: item's name field
- `{item_related_info}`: item's complete yaml content (name + category + description etc.)
- `{output_dir}`: execution.output_dir from outline.yaml (default: ./results)
- `{fields_path}`: absolute path to {topic}/fields.yaml
- `{output_path}`: absolute path to {output_dir}/{item_name_slug}.json
  - 한글 파일명 지원: 한글은 그대로 유지 (예: "GitHub_Copilot.json", "커서.json" 등)
  - 공백만 언더스코어로 변환, 특수문자 제거
- `{progress_file}`: execution.progress_file from outline.yaml (default: ./progress.json)

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

**Prompt Template**:
```python
prompt = f"""## Task
Research {item_related_info}, output structured JSON to {output_path}

## Field Definitions
Read {fields_path} to get all field definitions

## Output Requirements
1. Write JSON file to {output_path} (MUST save file, not just return content)
2. Output JSON according to fields defined in fields.yaml
3. Mark uncertain field values with [uncertain]
4. Add uncertain array at the end of JSON, listing all uncertain field names
5. For important fields, add source tracking:
   - _source: URL where information was found
   - _retrieved_at: ISO timestamp
6. Add research metadata at the end:
   - research_date: Current date
   - sources_checked: Number of sources consulted

## Output Path
{output_path}

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py -f {fields_path} -j {output_path}
Task is complete only after validation passes.
"""
```

**One-shot Example** (assuming researching GitHub Copilot):
```
## Task
Research name: GitHub Copilot
category: International Product
description: Developed by Microsoft/GitHub, first mainstream AI coding assistant, ~40% market share, output structured JSON to /home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json

## Field Definitions
Read /home/weizhena/AIcoding/aicoding-history/fields.yaml to get all field definitions

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at the end of JSON, listing all uncertain field names
4. All field values must be in English

## Output Path
/home/weizhena/AIcoding/aicoding-history/results/GitHub_Copilot.json

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py -f /path/to/fields.yaml -j /path/to/results/GitHub_Copilot.json
Task is complete only after validation passes.
```

### Step 4: Wait and Monitor
- Wait for current batch to complete
- Update progress.json after each item completes:
  ```json
  {
    "started_at": "2026-01-18T03:55:00",
    "total_items": 18,
    "completed_items": 9,
    "current_batch": 2,
    "items": {
      "GitHub_Copilot": "completed",
      "Cursor": "completed",
      "Windsurf": "in_progress"
    }
  }
  ```
- Launch next batch (need user approval)
- Display progress

### Step 5: Summary Report
After all complete, output:
- Completion count
- Failed/uncertain marked items
- Output directory

## Agent Config
- Background execution: Yes
- Task Output: Disabled (agent has explicit output file when complete)
- Resume support: Yes
