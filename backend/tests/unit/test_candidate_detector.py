import pytest

from app.analysis.candidate_detector import PythonCandidateDetector


DETECTION_SAMPLE = """
def process(data, value, extra):
    total = 0
    result = []
    if data:
        for item in data:
            if item > value:
                if extra:
                    total += item
                    result.append(item)
    if data:
        total += 1
    if data:
        total += 1
    temp = total
    thing = temp + value
    return thing
""".strip()


def test_candidate_detector_returns_ranked_candidates_without_executing_code():
    detector = PythonCandidateDetector()

    candidates = detector.detect(DETECTION_SAMPLE)

    assert [candidate.smell for candidate in candidates] == [
        "LongMethod",
        "DeepNesting",
        "DuplicatedCode",
    ]
    assert candidates[0].candidate_region == "lines 1-16"
    assert "process" in candidates[0].candidate_code


def test_candidate_detector_is_deterministic_for_same_input():
    detector = PythonCandidateDetector()

    first_pass = detector.detect(DETECTION_SAMPLE)
    second_pass = detector.detect(DETECTION_SAMPLE)

    assert first_pass == second_pass


def test_candidate_detector_rejects_invalid_python_safely():
    detector = PythonCandidateDetector()

    with pytest.raises(ValueError, match="Submitted code is not valid Python syntax"):
        detector.detect("def broken(:\n    pass\n")


def test_candidate_detector_can_inspect_candidate_metrics():
    detector = PythonCandidateDetector()

    metrics = detector.inspect_candidate_code(DETECTION_SAMPLE)

    assert metrics.line_span == 16
    assert metrics.statement_count == 15
    assert metrics.max_nesting == 4
    assert metrics.duplicate_statement_count == 1
    assert metrics.poor_names == ["process", "temp", "thing", "item"]
