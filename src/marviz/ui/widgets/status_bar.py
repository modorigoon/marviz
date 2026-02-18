from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label


class StatusBar(Vertical):
    """Status info — MDIR style."""

    BORDER_TITLE = " Status "

    def compose(self) -> ComposeResult:
        yield Label("[#ffff55]Model:[/]  claude-sonnet-4-20250514", id="status-model")
        yield Label("[#ffff55]Agents:[/] 0/3", id="status-agents")
        yield Label("[#ffff55]Tokens:[/] 0", id="status-tokens")
        yield Label("")
        yield Label("[#005555]Marviz v0.1.0[/]", id="status-version")
