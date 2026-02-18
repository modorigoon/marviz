from textual.app import ComposeResult
from textual.containers import Vertical

from .agent_panel import AgentPanel


class AgentContainer(Vertical):
    """Container for sub-agent panels — MDIR style."""

    BORDER_TITLE = " Sub-Agents "

    def compose(self) -> ComposeResult:
        yield AgentPanel("Worker-1", id="sub-agent-1")
        yield AgentPanel("Worker-2", id="sub-agent-2")
        yield AgentPanel("Worker-3", id="sub-agent-3")
