from __future__ import annotations

from typing import Literal

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import RichLog, Static


StatusType = Literal["idle", "working", "done", "error"]

_STATUS_STYLES = {
    "idle": "#005555",
    "working": "#ffff55",
    "done": "#55ff55",
    "error": "#ff5555",
}


class AgentPanel(Vertical):
    """Single sub-agent output panel with streaming and status support."""

    def __init__(self, agent_name: str = "Sub-Agent", **kwargs) -> None:
        super().__init__(**kwargs)
        self._agent_name = agent_name
        self._status: StatusType = "idle"
        self._assigned_agent_id: str | None = None
        self._stream_buffer: str = ""

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id=f"{self.id}-log")
        yield Static("", classes="agent-streaming")

    def on_mount(self) -> None:
        self.set_status("idle")

    def set_status(self, status: StatusType, label: str | None = None) -> None:
        self._status = status
        color = _STATUS_STYLES[status]
        name = label or self._agent_name
        self.border_title = f" {name} \u2500 {status} "
        log = self.query_one(RichLog)
        if status == "idle":
            log.clear()
            log.write(f"[{color}]{name} \u2500 idle[/]")

    def append_token(self, token: str) -> None:
        """Append a streamed token to the streaming buffer."""
        self._stream_buffer += token
        static = self.query_one(".agent-streaming", Static)
        static.update(self._stream_buffer)

    def finish_response(self) -> None:
        """Flush streaming buffer to permanent log."""
        if self._stream_buffer:
            log = self.query_one(RichLog)
            log.write(self._stream_buffer)
            self._stream_buffer = ""
            static = self.query_one(".agent-streaming", Static)
            static.update("")

    def show_error(self, message: str) -> None:
        self.finish_response()
        log = self.query_one(RichLog)
        log.write(f"[#ff5555]ERROR: {message}[/]")
        self.set_status("error")

    def reset(self) -> None:
        """Clear all content and return to idle."""
        self._stream_buffer = ""
        self._assigned_agent_id = None
        log = self.query_one(RichLog)
        log.clear()
        static = self.query_one(".agent-streaming", Static)
        static.update("")
        self.set_status("idle")
