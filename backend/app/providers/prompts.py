from app.providers.contracts import (
    CandidateClassificationInput,
    ExerciseGenerationInput,
    HintGenerationInput,
)


def classification_prompt(payload: CandidateClassificationInput) -> str:
    guidance = guidance_block(payload.guidance_snippets)
    expected_label = payload.heuristic_label or "LongMethod"
    return (
        "You are classifying one refactor candidate for a refactoring practice app.\n"
        "Return only JSON with keys label and rationale.\n"
        f"The label should stay aligned with the heuristic label '{expected_label}' unless the"
        " candidate clearly suggests a more precise smell.\n"
        f"Language: {payload.language}\n"
        f"Candidate region: {payload.candidate_region}\n"
        f"Detection summary: {payload.detection_summary}\n"
        f"Candidate code:\n{payload.candidate_code}\n"
        f"{guidance}"
    )


def exercise_prompt(payload: ExerciseGenerationInput) -> str:
    guidance = guidance_block(payload.guidance_snippets)
    return (
        "You are writing one refactoring exercise.\n"
        "Return only JSON with keys title, description, and difficulty.\n"
        "Difficulty must be one of Easy, Medium, or Hard.\n"
        "Do not reveal final code.\n"
        f"Language: {payload.language}\n"
        f"Issue label: {payload.issue_label}\n"
        f"Candidate region: {payload.candidate_region}\n"
        f"Classification rationale: {payload.classification_rationale}\n"
        f"Candidate code:\n{payload.candidate_code}\n"
        f"{guidance}"
    )


def hint_prompt(payload: HintGenerationInput) -> str:
    guidance = guidance_block(payload.guidance_snippets)
    return (
        "You are writing one progressive refactoring hint.\n"
        "Return only JSON with the key hint.\n"
        "Do not reveal final code or a full step-by-step solution.\n"
        f"Language: {payload.language}\n"
        f"Hint level: {payload.hint_level}\n"
        f"Exercise title: {payload.exercise_title}\n"
        f"Exercise description: {payload.exercise_description}\n"
        f"Issue label: {payload.issue_label}\n"
        f"Candidate code:\n{payload.candidate_code}\n"
        f"{guidance}"
    )


def guidance_block(guidance_snippets: list[str]) -> str:
    if not guidance_snippets:
        return "Guidance: stay within the shared provider contract."
    return "Guidance:\n- " + "\n- ".join(guidance_snippets)
