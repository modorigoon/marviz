from __future__ import annotations

from collections.abc import AsyncIterator

from ..providers.base import BaseProvider
from .types import AccumulatedToolCall, StreamChunk, ToolCallAccumulator


class BaseAgent:
    """Base agent with conversation history and streaming."""

    def __init__(self, provider: BaseProvider, system_prompt: str) -> None:
        self.provider = provider
        self.history: list[dict] = [{"role": "system", "content": system_prompt}]
        self.pending_tool_calls: list[AccumulatedToolCall] = []

    async def send(
        self,
        user_input: str,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Send user input and stream back chunks. Updates history."""
        self.history.append({"role": "user", "content": user_input})
        self.pending_tool_calls.clear()

        full_response = ""
        accumulator = ToolCallAccumulator()

        async for chunk in self.provider.stream(self.history, tools=tools):
            if chunk.type == "text":
                full_response += chunk.content
            elif chunk.type == "tool_call":
                accumulator.feed(chunk)
            yield chunk

        # Build assistant message for history
        if full_response or accumulator._calls:
            msg: dict = {"role": "assistant", "content": full_response or None}
            accumulated = accumulator.finalize()
            if accumulated:
                msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": __import__("json").dumps(tc.arguments),
                        },
                    }
                    for tc in accumulated
                ]
                self.pending_tool_calls = accumulated
            self.history.append(msg)

    def add_tool_result(self, tool_call_id: str, result: str) -> None:
        """Inject a tool result into the conversation history."""
        self.history.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": result,
            }
        )

    async def continue_after_tools(
        self,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        """Resume LLM generation after tool results have been added."""
        self.pending_tool_calls.clear()
        full_response = ""
        accumulator = ToolCallAccumulator()

        async for chunk in self.provider.stream(self.history, tools=tools):
            if chunk.type == "text":
                full_response += chunk.content
            elif chunk.type == "tool_call":
                accumulator.feed(chunk)
            yield chunk

        if full_response or accumulator._calls:
            msg: dict = {"role": "assistant", "content": full_response or None}
            accumulated = accumulator.finalize()
            if accumulated:
                msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": __import__("json").dumps(tc.arguments),
                        },
                    }
                    for tc in accumulated
                ]
                self.pending_tool_calls = accumulated
            self.history.append(msg)
