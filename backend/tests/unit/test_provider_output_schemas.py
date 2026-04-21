import pytest
from pydantic import ValidationError

from app.providers.contracts import (
    CandidateClassificationResult,
    ExerciseGenerationResult,
    HintGenerationResult,
)
from app.providers.json_schema import strict_json_schema


def test_classification_output_schema_accepts_required_shape():
    result = CandidateClassificationResult.model_validate(
        {
            "label": "LongMethod",
            "rationale": "The function mixes multiple responsibilities.",
        }
    )

    assert result.label == "LongMethod"
    assert result.rationale.startswith("The function")


def test_classification_output_schema_rejects_missing_required_field():
    with pytest.raises(ValidationError):
        CandidateClassificationResult.model_validate({"label": "LongMethod"})


def test_exercise_output_schema_accepts_required_shape():
    result = ExerciseGenerationResult.model_validate(
        {
            "title": "Break up the long method",
            "description": "Reduce the number of responsibilities in the selected function.",
            "difficulty": "Medium",
        }
    )

    assert result.difficulty == "Medium"


def test_exercise_output_schema_rejects_invalid_difficulty():
    with pytest.raises(ValidationError):
        ExerciseGenerationResult.model_validate(
            {
                "title": "Break up the long method",
                "description": "Reduce the number of responsibilities.",
                "difficulty": "Expert",
            }
        )


def test_hint_output_schema_accepts_required_shape():
    result = HintGenerationResult.model_validate(
        {"hint": "Look for one responsibility boundary before editing names."}
    )

    assert "responsibility" in result.hint


def test_hint_output_schema_rejects_missing_hint_text():
    with pytest.raises(ValidationError):
        HintGenerationResult.model_validate({})


def test_provider_output_json_schemas_disallow_extra_top_level_fields():
    for result_type in (
        CandidateClassificationResult,
        ExerciseGenerationResult,
        HintGenerationResult,
    ):
        schema = strict_json_schema(result_type)

        assert schema["additionalProperties"] is False
