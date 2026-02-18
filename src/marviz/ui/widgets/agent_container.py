from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical

from .agent_panel import AgentPanel


PANEL_IDS = ["sub-agent-1", "sub-agent-2", "sub-agent-3"]


class AgentContainer(Vertical):
    """Container for sub-agent panels with slot management."""

    BORDER_TITLE = " Sub-Agents "

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._assignments: dict[str, str] = {}  # agent_id -> panel_id

    def compose(self) -> ComposeResult:
        yield AgentPanel("Worker-1", id="sub-agent-1")
        yield AgentPanel("Worker-2", id="sub-agent-2")
        yield AgentPanel("Worker-3", id="sub-agent-3")

    def claim_panel(self, agent_id: str, name: str) -> str | None:
        """Assign an idle panel to an agent. Returns panel_id or None if full."""
        if agent_id in self._assignments:
            return self._assignments[agent_id]

        occupied = set(self._assignments.values())
        for pid in PANEL_IDS:
            if pid not in occupied:
                self._assignments[agent_id] = pid
                panel = self.query_one(f"#{pid}", AgentPanel)
                panel._assigned_agent_id = agent_id
                panel.reset()
                panel._agent_name = name
                panel.set_status("working", label=name)
                return pid
        return None

    def release_panel(self, agent_id: str) -> None:
        """Release a panel slot back to idle."""
        pid = self._assignments.pop(agent_id, None)
        if pid:
            panel = self.query_one(f"#{pid}", AgentPanel)
            panel._assigned_agent_id = None
            panel.set_status("idle")

    def get_panel(self, agent_id: str) -> AgentPanel | None:
        """Get the panel assigned to an agent."""
        pid = self._assignments.get(agent_id)
        if pid:
            return self.query_one(f"#{pid}", AgentPanel)
        return None

    @property
    def active_count(self) -> int:
        return len(self._assignments)
