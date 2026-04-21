import pytest

from app.guidance.base import GuidanceRequest, GuidanceRetriever, GuidanceSnippet
from app.guidance.local import LocalGuidanceRetriever
from app.providers.mock import MockProvider
from app.schemas.api import SubmitAttemptRequest, SubmitCodeRequest
from app.services.candidate_service import CandidateService
from app.services.exercise_service import ExerciseService
from app.services.provider_service import ProviderService
from app.storage.memory import app_state


def test_exercise_service_generates_one_exercise_for_selected_candidate():
    service, candidate_id = build_exercise_service()

    response = service.create_exercise(candidate_id)

    assert response.candidate_id == candidate_id
    assert response.status == "generated"
    assert response.title == "Practice improving PoorNaming"
    assert response.difficulty == "Medium"
    assert app_state.exercises[response.exercise_id]["classification_rationale"].startswith(
        "Mock provider classification based on deterministic detection summary:"
    )


def test_exercise_service_rejects_unknown_candidate():
    service = ExerciseService(
        guidance_retriever=LocalGuidanceRetriever(),
        provider_service=ProviderService(providers=[MockProvider()]),
    )

    with pytest.raises(LookupError, match="Candidate 'cand-missing' was not found."):
        service.create_exercise("cand-missing")


def test_exercise_service_reveals_one_new_hint_per_request():
    service, candidate_id = build_exercise_service()
    exercise = service.create_exercise(candidate_id)

    first_hint = service.generate_hints(exercise.exercise_id)
    second_hint = service.generate_hints(exercise.exercise_id)
    third_hint = service.generate_hints(exercise.exercise_id)

    assert first_hint.hints == [
        "Start by isolating the part of the code that shows the PoorNaming smell."
    ]
    assert second_hint.hints == [
        "Start by isolating the part of the code that shows the PoorNaming smell.",
        "Extract one cohesive responsibility first, then reassess whether the main flow reads more clearly.",
    ]
    assert third_hint.hints == second_hint.hints
    assert app_state.exercises[exercise.exercise_id]["revealed_hints"] == second_hint.hints


def test_exercise_service_blocks_hint_leakage():
    class LeakyProvider(MockProvider):
        def generateHints(self, payload):
            class Result:
                hint = "```python\ndef solved():\n    return 1\n```"

            return Result()

    service, candidate_id = build_exercise_service(provider=LeakyProvider())
    exercise = service.create_exercise(candidate_id)

    with pytest.raises(RuntimeError, match="Generated hint violated leakage guardrails."):
        service.generate_hints(exercise.exercise_id)


def test_exercise_service_blocks_unfenced_full_refactored_code_hint():
    class FullCodeProvider(MockProvider):
        def generateHints(self, payload):
            class Result:
                hint = (
                    "def clarify_names(records, threshold):\n"
                    "    running_total = 0\n"
                    "    increment = threshold + 1\n"
                    "    return running_total + increment"
                )

            return Result()

    service, candidate_id = build_exercise_service(provider=FullCodeProvider())
    exercise = service.create_exercise(candidate_id)

    with pytest.raises(RuntimeError, match="Generated hint violated leakage guardrails."):
        service.generate_hints(exercise.exercise_id)


def test_exercise_service_blocks_full_solution_explanation_hint():
    class FullSolutionProvider(MockProvider):
        def generateHints(self, payload):
            class Result:
                hint = (
                    "1. Rename process to clarify_names. "
                    "2. Rename data to records. "
                    "3. Rename value to threshold. "
                    "4. Rename thing to increment."
                )

            return Result()

    service, candidate_id = build_exercise_service(provider=FullSolutionProvider())
    exercise = service.create_exercise(candidate_id)

    with pytest.raises(RuntimeError, match="Generated hint violated leakage guardrails."):
        service.generate_hints(exercise.exercise_id)


def test_exercise_service_accepts_attempt_when_targeted_signal_improves():
    service, candidate_id = build_exercise_service()
    exercise = service.create_exercise(candidate_id)

    response = service.submit_attempt(
        exercise.exercise_id,
        SubmitAttemptRequest(
            attempt_code=(
                "def clarify_names(records, threshold):\n"
                "    running_total = 0\n"
                "    increment = threshold + 1\n"
                "    return running_total + increment\n"
            )
        ),
    )

    assert response.accepted is True
    assert response.status == "evaluated"
    assert response.feedback == (
        "The targeted PoorNaming signal was reduced and the code still parses."
    )


def test_exercise_service_rejects_invalid_or_unchanged_attempts():
    service, candidate_id = build_exercise_service()
    exercise = service.create_exercise(candidate_id)

    invalid_response = service.submit_attempt(
        exercise.exercise_id,
        SubmitAttemptRequest(attempt_code="def broken(:\n    pass\n"),
    )
    unchanged_response = service.submit_attempt(
        exercise.exercise_id,
        SubmitAttemptRequest(
            attempt_code=(
                "def process(data, value):\n"
                "    total = 0\n"
                "    thing = value + 1\n"
                "    return total + thing\n"
            )
        ),
    )

    assert invalid_response.accepted is False
    assert invalid_response.feedback == "The submitted attempt does not parse as valid Python yet."
    assert unchanged_response.accepted is False
    assert unchanged_response.feedback == (
        "The submitted attempt is unchanged from the original candidate region."
    )


def test_exercise_service_supplies_guidance_snippets_and_fallbacks():
    class RecordingProvider(MockProvider):
        def __init__(self) -> None:
            self.classification_inputs = []
            self.exercise_inputs = []
            self.hint_inputs = []

        def classifyCandidate(self, payload):
            self.classification_inputs.append(payload)
            return super().classifyCandidate(payload)

        def generateExercise(self, payload):
            self.exercise_inputs.append(payload)
            return super().generateExercise(payload)

        def generateHints(self, payload):
            self.hint_inputs.append(payload)
            return super().generateHints(payload)

    class SparseGuidanceRetriever(GuidanceRetriever):
        def getGuidance(self, payload: GuidanceRequest) -> list[GuidanceSnippet]:
            if payload.query == "missing-topic":
                return [
                    GuidanceSnippet(
                        topic="refactoring_principles",
                        summary="# Refactoring Principles",
                        content="# Refactoring Principles\nPrefer readability over cleverness.\n",
                        source="local",
                    )
                ]
            return []

    provider = RecordingProvider()
    service, candidate_id = build_exercise_service(
        provider=provider,
        guidance_retriever=SparseGuidanceRetriever(),
    )
    exercise = service.create_exercise(candidate_id)
    service.generate_hints(exercise.exercise_id)

    assert provider.classification_inputs[0].guidance_snippets == [
        "refactoring_principles: Prefer readability over cleverness."
    ]
    assert provider.exercise_inputs[0].guidance_snippets == [
        "refactoring_principles: Prefer readability over cleverness."
    ]
    assert provider.hint_inputs[0].guidance_snippets == [
        "refactoring_principles: Prefer readability over cleverness."
    ]


def build_exercise_service(
    provider: MockProvider | None = None,
    guidance_retriever: GuidanceRetriever | None = None,
) -> tuple[ExerciseService, str]:
    candidate_service = CandidateService()
    submission = candidate_service.submit_code(
        SubmitCodeRequest(
            source="paste",
            filename="exercise.py",
            code=(
                "def process(data, value):\n"
                "    total = 0\n"
                "    thing = value + 1\n"
                "    return total + thing\n"
            ),
        )
    )
    candidate_id = candidate_service.list_candidates(submission.submission_id).candidates[0].id
    service = ExerciseService(
        guidance_retriever=guidance_retriever or LocalGuidanceRetriever(),
        provider_service=ProviderService(providers=[provider or MockProvider()]),
    )
    return service, candidate_id
