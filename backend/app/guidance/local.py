from app.guidance.base import GuidanceRetriever
from app.guidance.catalog import GUIDANCE_TOPICS


class LocalGuidanceRetriever(GuidanceRetriever):
    def getGuidance(self, topic: str) -> dict:
        path = GUIDANCE_TOPICS.get(topic)
        if not path or not path.exists():
            return {
                "topic": topic,
                "summary": "Guidance topic not found in local docs.",
                "content": "",
                "source": "local",
            }

        content = path.read_text(encoding="utf-8")
        summary_line = next((line.strip() for line in content.splitlines() if line.strip()), "Placeholder guidance")
        return {
            "topic": topic,
            "summary": summary_line,
            "content": content,
            "source": "local",
        }

