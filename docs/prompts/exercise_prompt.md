# Exercise Prompt

## Purpose

Use this prompt to generate one exercise brief for a classified candidate without revealing the answer.

## Required Inputs

- language
- candidate code snippet
- line range or region metadata
- selected taxonomy label
- classification rationale
- classification difficulty
- relevant refactoring principles
- relevant exercise authoring rules
- relevant difficulty rubric snippets

## System Prompt

```text
You are generating a refactoring exercise.

Follow the provided refactoring principles and exercise authoring rules strictly.
Target one primary issue.
Describe what to improve and why it matters.
Return a separate rationale field.
Do not provide solutions, final code, or a single required final structure.
Output JSON only.
```

## User Prompt Template

````text
Language: {{language}}
Candidate region: {{line_range}}
Issue label: {{issue_label}}
Classification rationale: {{classification_rationale}}
Classification difficulty: {{classification_difficulty}}

Applicable guidance:
{{guidance_snippets}}

Code:
```{{language}}
{{candidate_code}}
```

Generate one refactoring exercise for this candidate.

Return:
{
  "title": "",
  "description": "",
  "rationale": "",
  "difficulty": ""
}
````

## Output Contract

```json
{
  "title": "Improve readability in a multi-purpose function",
  "description": "Refactor this function to reduce responsibility overlap and make the main flow easier to follow.",
  "rationale": "The current structure mixes concerns and makes the function harder to understand and change safely.",
  "difficulty": "Medium"
}
```

## Validation Rules

- `title` must be concise and task-oriented.
- `description` must describe the improvement goal without prescribing the full implementation.
- `rationale` must explain why the issue matters without revealing the finished design.
- `difficulty` must be one of `Easy`, `Medium`, or `Hard`.
- No extra properties are allowed.
- Any output outside valid JSON should be rejected.
