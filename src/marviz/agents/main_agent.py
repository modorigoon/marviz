from __future__ import annotations

from collections.abc import AsyncIterator

from ..providers.base import BaseProvider
from .base import BaseAgent
from .types import StreamChunk

DELEGATE_TASK_TOOL = {
    "type": "function",
    "function": {
        "name": "delegate_task",
        "description": (
            "Delegate a self-contained sub-task to a worker agent. "
            "Each worker runs independently and streams its output to a dedicated panel. "
            "Use this when the user's request can be split into parallel sub-tasks. "
            "Maximum 3 concurrent workers."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "Clear, self-contained task description for the worker.",
                },
                "worker_name": {
                    "type": "string",
                    "description": "Short label for the worker panel (e.g. 'Analyzer', 'Coder').",
                },
            },
            "required": ["task", "worker_name"],
        },
    },
}

WRITE_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": (
            "Write content to a file. Creates the file and parent directories if they don't exist. "
            "Overwrites the file if it already exists."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path (relative to working directory or absolute).",
                },
                "content": {
                    "type": "string",
                    "description": "Full content to write to the file.",
                },
            },
            "required": ["path", "content"],
        },
    },
}

READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the content of a file and return it.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path to read.",
                },
            },
            "required": ["path"],
        },
    },
}

TOOLS = [DELEGATE_TASK_TOOL, WRITE_FILE_TOOL, READ_FILE_TOOL]


class MainAgent(BaseAgent):
    """Primary conversational agent for Marviz."""

    SYSTEM_PROMPT = (
        "You are Marviz, an AI development assistant running inside a "
        "terminal environment. Be concise, helpful, and precise. "
        "Format your responses for terminal readability.\n\n"
        "## Tools\n\n"
        "### delegate_task\n"
        "Delegate independent sub-tasks to worker agents (up to 3 parallel). "
        "Each worker executes in parallel and reports back. "
        "After all workers finish, summarize their combined results. "
        "Only delegate when the request genuinely benefits from parallel work.\n\n"
        "### write_file\n"
        "Write content to a file. Use this to create or overwrite files. "
        "You can combine with delegate_task: delegate sub-tasks first, "
        "then write the combined results to a file.\n\n"
        "### read_file\n"
        "Read the content of a file. Use this to inspect existing files.\n\n"
        "For simple questions, answer directly without using any tools."
    )

    def __init__(self, provider: BaseProvider) -> None:
        super().__init__(provider, self.SYSTEM_PROMPT)

    async def send(
        self,
        user_input: str,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        effective_tools = tools if tools is not None else TOOLS
        async for chunk in super().send(user_input, tools=effective_tools):
            yield chunk

    async def continue_after_tools(
        self,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[StreamChunk]:
        effective_tools = tools if tools is not None else TOOLS
        async for chunk in super().continue_after_tools(tools=effective_tools):
            yield chunk
