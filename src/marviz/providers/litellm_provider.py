from __future__ import annotations

from collections.abc import AsyncIterator

import litellm

from ..agents.types import StreamChunk
from .base import BaseProvider


class LiteLLMProvider(BaseProvider):
    """LiteLLM-backed provider with async streaming."""

    def __init__(self, model: str) -> None:
        self.model = model

    async def stream(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        try:
            kwargs: dict = dict(
                model=self.model,
                messages=messages,
                stream=True,
            )
            if tools:
                kwargs["tools"] = tools

            response = await litellm.acompletion(**kwargs)

            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield StreamChunk(type="text", content=delta.content)
                if getattr(delta, "tool_calls", None):
                    for tc in delta.tool_calls:
                        yield StreamChunk(
                            type="tool_call",
                            tool_name=tc.function.name if tc.function and tc.function.name else None,
                            tool_args=tc.function.arguments if tc.function and tc.function.arguments else None,
                            tool_call_id=getattr(tc, "id", None),
                            tool_call_index=getattr(tc, "index", None),
                        )
        except Exception as exc:
            yield StreamChunk(type="error", content=str(exc))
