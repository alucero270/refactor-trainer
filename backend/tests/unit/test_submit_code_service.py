from app.schemas.api import SubmitCodeRequest
from app.services.candidate_service import CandidateService
from app.storage.memory import app_state


def test_submit_code_normalizes_python_submission_for_downstream_use():
    service = CandidateService()

    response = service.submit_code(
        SubmitCodeRequest(
            source="paste",
            filename="example.py",
            code="\ufeffdef example():\r\n    return 1",
        )
    )

    stored_submission = app_state.submissions[response.submission_id]

    assert response.status == "accepted"
    assert response.candidate_count == 0
    assert stored_submission["filename"] == "example.py"
    assert stored_submission["language"] == "python"
    assert stored_submission["code"] == "def example():\n    return 1\n"
    assert stored_submission["candidates"] == []


def test_submit_code_defaults_paste_filename_to_single_python_file():
    service = CandidateService()

    response = service.submit_code(
        SubmitCodeRequest(
            source="paste",
            code="print('hello')",
        )
    )

    assert app_state.submissions[response.submission_id]["filename"] == "snippet.py"


def test_submit_code_rejects_inputs_outside_single_file_boundary():
    service = CandidateService()

    try:
        service.submit_code(
            SubmitCodeRequest(
                source="upload",
                filename="nested/example.txt",
                code="print('hello')",
            )
        )
    except ValueError as exc:
        assert str(exc) == "submit-code accepts exactly one Python file, not a file path."
    else:
        raise AssertionError("Expected invalid single-file submission to be rejected.")
