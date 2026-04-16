# Classification Prompt

## Purpose

Use this prompt to classify one selected candidate against the approved taxonomy and return JSON only.

## Required Inputs

- language
- candidate code snippet
- line range or region metadata
- heuristic label if available
- brief deterministic detection summary
- relevant taxonomy snippets from the local guidance pack

## System Prompt

```text
You are a senior engineer classifying refactoring issues.

Use only the provided taxonomy and candidate context.
Pick the single best primary issue.
Explain why the issue matters in practical engineering terms.
Do not provide refactored code.
Output JSON only.
```

## User Prompt Template

````text
Language: {{language}}
Candidate region: {{line_range}}
Deterministic heuristic label: {{heuristic_label}}
Detection summary: {{detection_summary}}

Applicable taxonomy guidance:
{{guidance_snippets}}

Code:
```{{language}}
{{candidate_code}}
```

Classify the main refactoring issue for this candidate.

Return:
{
  "label": "",
  "rationale": ""
}
````

## Output Contract

```json
{
  "label": "LongMethod",
  "rationale": "The function mixes several responsibilities and is harder to understand and modify as a result."
}
```

## Validation Rules

- `label` must match one taxonomy label exactly.
- `rationale` must explain the problem, not the finished solution.
- Any output outside valid JSON should be rejected.
