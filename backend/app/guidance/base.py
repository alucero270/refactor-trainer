from abc import ABC, abstractmethod


class GuidanceRetriever(ABC):
    @abstractmethod
    def getGuidance(self, topic: str) -> dict:
        """Return guidance content for a topic.

        This abstraction intentionally leaves room for a future
        McpStrataGuidanceRetriever without coupling the scaffold to it now.
        """

