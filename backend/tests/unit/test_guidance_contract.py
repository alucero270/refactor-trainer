from app.guidance.local import LocalGuidanceRetriever


def test_local_guidance_retriever_returns_local_content():
    retriever = LocalGuidanceRetriever()

    guidance = retriever.getGuidance("refactoring_principles")

    assert guidance["source"] == "local"
    assert "Refactoring Principles" in guidance["content"]


def test_local_guidance_retriever_handles_missing_topics():
    retriever = LocalGuidanceRetriever()

    guidance = retriever.getGuidance("missing-topic")

    assert guidance["source"] == "local"
    assert guidance["content"] == ""

