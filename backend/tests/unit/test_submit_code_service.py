import pytest

from app.schemas.api import SubmitCodeRequest
from app.services.candidate_service import CandidateService
from app.storage.memory import app_state


def test_submit_code_normalizes_python_submission_for_downstream_use():
    service = CandidateService()

    response = service.submit_code(
        SubmitCodeRequest(
            source="paste",
            filename="example.py",
            code="\ufeffdef process(data, value):\r\n    total = 0\r\n    thing = value + 1\r\n    return total + thing",
        )
    )

    stored_submission = app_state.submissions[response.submission_id]

    assert response.status == "accepted"
    assert response.candidate_count == 1
    assert stored_submission["filename"] == "example.py"
    assert stored_submission["language"] == "python"
    assert stored_submission["code"] == (
        "def process(data, value):\n    total = 0\n    thing = value + 1\n    return total + thing\n"
    )
    assert stored_submission["candidates"] == []
    assert stored_submission["detected_candidates"][0]["smell"] == "PoorNaming"


def test_submit_code_defaults_paste_filename_to_single_python_file():
    service = CandidateService()

    response = service.submit_code(
        SubmitCodeRequest(
            source="paste",
            code="print('hello')",
        )
    )

    assert app_state.submissions[response.submission_id]["filename"] == "snippet.py"
    assert app_state.submissions[response.submission_id]["detected_candidates"] == []


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


def test_submit_code_rejects_invalid_python_before_storing_submission():
    service = CandidateService()

    with pytest.raises(ValueError, match="Submitted code is not valid Python syntax"):
        service.submit_code(
            SubmitCodeRequest(
                source="paste",
                filename="broken.py",
                code="def broken(:\n    pass\n",
            )
        )

    assert app_state.submissions == {}


def test_list_candidates_returns_public_candidates_in_detected_order():
    service = CandidateService()

    response = service.submit_code(
        SubmitCodeRequest(
            source="paste",
            filename="example.py",
            code=(
                "def process(data, value, extra):\n"
                "    total = 0\n"
                "    result = []\n"
                "    if data:\n"
                "        for item in data:\n"
                "            if item > value:\n"
                "                if extra:\n"
                "                    total += item\n"
                "                    result.append(item)\n"
                "    if data:\n"
                "        total += 1\n"
                "    if data:\n"
                "        total += 1\n"
                "    temp = total\n"
                "    thing = temp + value\n"
                "    return thing\n"
            ),
        )
    )

    listed = service.list_candidates(response.submission_id)

    assert [candidate.smell for candidate in listed.candidates] == [
        "LongMethod",
        "DeepNesting",
        "DuplicatedCode",
    ]
    assert app_state.submissions[response.submission_id]["candidates"][0] == {
        "id": "cand-longmethod-process-1",
        "title": "Break up long function 'process'",
        "smell": "LongMethod",
        "summary": (
            "Function 'process' spans 16 lines across 15 statements, "
            "which suggests multiple responsibilities."
        ),
        "severity": "high",
    }
