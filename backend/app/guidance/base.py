from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class GuidanceRequest(BaseModel):
    language: str
    query: str
    maxSnippets: int = Field(..., gt=0)
    issueType: str | None = None
    difficulty: str | None = None


class GuidanceSnippet(BaseModel):
    topic: str
    summary: str
    content: str
    source: str


class GuidanceRetriever(ABC):
    @abstractmethod
    def getGuidance(self, payload: GuidanceRequest) -> list[GuidanceSnippet]:
        """Return rule-based local guidance snippets for prompt construction.

        This abstraction intentionally leaves room for a future
        McpStrataGuidanceRetriever without coupling the scaffold to it now.
        """
