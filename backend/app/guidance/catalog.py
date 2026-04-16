from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
GUIDANCE_ROOT = REPO_ROOT / "docs" / "guidance"

GUIDANCE_TOPICS = {
    "refactoring_principles": GUIDANCE_ROOT / "refactoring_principles.md",
    "code_smell_taxonomy": GUIDANCE_ROOT / "code_smell_taxonomy.md",
    "exercise_authoring_rules": GUIDANCE_ROOT / "exercise_authoring_rules.md",
    "hint_policy": GUIDANCE_ROOT / "hint_policy.md",
    "difficulty_rubric": GUIDANCE_ROOT / "difficulty_rubric.md",
}

