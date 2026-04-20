import pytest

from app.guidance.local import LocalGuidanceRetriever
from app.providers.mock import MockProvider
from app.schemas.api import SubmitCodeRequest
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


def build_exercise_service(provider: MockProvider | None = None) -> tuple[ExerciseService, str]:
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
        guidance_retriever=LocalGuidanceRetriever(),
        provider_service=ProviderService(providers=[provider or MockProvider()]),
    )
    return service, candidate_id
