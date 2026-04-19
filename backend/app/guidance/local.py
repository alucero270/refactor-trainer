from app.guidance.base import GuidanceRequest, GuidanceRetriever, GuidanceSnippet
from app.guidance.catalog import GUIDANCE_TOPICS


class LocalGuidanceRetriever(GuidanceRetriever):
    fallback_topic = "refactoring_principles"

    def getGuidance(self, payload: GuidanceRequest) -> list[GuidanceSnippet]:
        topics = self._resolve_topics(payload)
        return [self._load_snippet(topic) for topic in topics[: payload.maxSnippets]]

    def _resolve_topics(self, payload: GuidanceRequest) -> list[str]:
        topics: list[str] = []

        if payload.query in GUIDANCE_TOPICS:
            topics.append(payload.query)

        if payload.issueType:
            topics.append("code_smell_taxonomy")

        if payload.difficulty:
            topics.append("difficulty_rubric")

        deduped_topics = list(dict.fromkeys(topics))
        if deduped_topics:
            return deduped_topics

        return [self.fallback_topic]

    def _load_snippet(self, topic: str) -> GuidanceSnippet:
        path = GUIDANCE_TOPICS.get(topic)
        if not path or not path.exists():
            path = GUIDANCE_TOPICS[self.fallback_topic]
            topic = self.fallback_topic

        content = path.read_text(encoding="utf-8")
        summary_line = next((line.strip() for line in content.splitlines() if line.strip()), "Placeholder guidance")
        return GuidanceSnippet(
            topic=topic,
            summary=summary_line,
            content=content,
            source="local",
        )
