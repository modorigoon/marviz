from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from ..agents.types import StreamChunk


class BaseProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    async def stream(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Yield streaming chunks from the LLM."""
        ...  # pragma: no cover
