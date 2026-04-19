from app.guidance.base import GuidanceRequest
from app.guidance.local import LocalGuidanceRetriever


def test_local_guidance_retriever_returns_local_content():
    retriever = LocalGuidanceRetriever()

    guidance = retriever.getGuidance(
        GuidanceRequest(language="python", query="refactoring_principles", maxSnippets=1)
    )

    assert len(guidance) == 1
    assert guidance[0].topic == "refactoring_principles"
    assert guidance[0].summary == "# Refactoring Principles"
    assert guidance[0].source == "local"
    assert "Refactoring Principles" in guidance[0].content


def test_local_guidance_retriever_includes_rule_based_context_topics():
    retriever = LocalGuidanceRetriever()

    guidance = retriever.getGuidance(
        GuidanceRequest(
            language="python",
            query="exercise_authoring_rules",
            issueType="LongMethod",
            difficulty="Medium",
            maxSnippets=3,
        )
    )

    assert [snippet.topic for snippet in guidance] == [
        "exercise_authoring_rules",
        "code_smell_taxonomy",
        "difficulty_rubric",
    ]


def test_local_guidance_retriever_handles_missing_topics():
    retriever = LocalGuidanceRetriever()

    guidance = retriever.getGuidance(
        GuidanceRequest(language="python", query="missing-topic", maxSnippets=1)
    )

    assert guidance[0].source == "local"
    assert guidance[0].topic == "refactoring_principles"
    assert "Refactoring Principles" in guidance[0].content
