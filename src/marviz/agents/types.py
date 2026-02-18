from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class StreamChunk:
    """A single chunk from a streaming LLM response."""

    type: Literal["text", "tool_call", "error"]
    content: str = ""
    tool_name: str | None = None
    tool_args: str | None = None  # raw JSON fragment (accumulated externally)
    tool_call_id: str | None = None
    tool_call_index: int | None = None


@dataclass
class AgentMessage:
    """A message in the agent conversation history."""

    role: Literal["user", "assistant"]
    content: str


@dataclass
class AccumulatedToolCall:
    """A fully-assembled tool call after fragment accumulation."""

    id: str
    name: str
    arguments: dict


class ToolCallAccumulator:
    """Collects streamed tool_call fragments and yields complete calls."""

    def __init__(self) -> None:
        self._calls: dict[int, dict] = {}  # index -> {id, name, args_buffer}

    def feed(self, chunk: StreamChunk) -> None:
        """Feed a tool_call chunk. Fragments are keyed by tool_call_index."""
        if chunk.type != "tool_call":
            return
        idx = chunk.tool_call_index or 0
        if idx not in self._calls:
            self._calls[idx] = {"id": None, "name": "", "args_buffer": ""}
        entry = self._calls[idx]
        if chunk.tool_call_id:
            entry["id"] = chunk.tool_call_id
        if chunk.tool_name:
            entry["name"] = chunk.tool_name
        if chunk.tool_args:
            entry["args_buffer"] += chunk.tool_args

    def finalize(self) -> list[AccumulatedToolCall]:
        """Parse all collected fragments into AccumulatedToolCall objects."""
        results: list[AccumulatedToolCall] = []
        for _idx in sorted(self._calls):
            entry = self._calls[_idx]
            try:
                args = json.loads(entry["args_buffer"]) if entry["args_buffer"] else {}
            except json.JSONDecodeError:
                args = {"_raw": entry["args_buffer"]}
            results.append(
                AccumulatedToolCall(
                    id=entry["id"] or f"call_{_idx}",
                    name=entry["name"],
                    arguments=args,
                )
            )
        self._calls.clear()
        return results
