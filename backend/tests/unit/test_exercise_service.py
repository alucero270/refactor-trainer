import pytest

from app.guidance.local import LocalGuidanceRetriever
from app.providers.mock import MockProvider
from app.schemas.api import SubmitCodeRequest
from app.services.candidate_service import CandidateService
from app.services.exercise_service import ExerciseService
from app.services.provider_service import ProviderService
from app.storage.memory import app_state


def test_exercise_service_generates_one_exercise_for_selected_candidate():
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
        provider_service=ProviderService(providers=[MockProvider()]),
    )

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
