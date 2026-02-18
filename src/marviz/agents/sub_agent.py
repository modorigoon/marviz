from __future__ import annotations

from ..providers.base import BaseProvider
from .base import BaseAgent


class SubAgent(BaseAgent):
    """Focused worker agent for a single delegated task."""

    SYSTEM_PROMPT = (
        "You are a focused worker agent inside the Marviz terminal environment. "
        "You have been assigned a specific task. Complete it thoroughly and concisely. "
        "Format your output for terminal readability. "
        "Do not ask follow-up questions — just execute the task."
    )

    def __init__(
        self,
        provider: BaseProvider,
        agent_id: str,
        worker_name: str,
        task: str,
    ) -> None:
        super().__init__(provider, self.SYSTEM_PROMPT)
        self.agent_id = agent_id
        self.worker_name = worker_name
        self.task = task
