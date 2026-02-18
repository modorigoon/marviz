from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label


class StatusBar(Vertical):
    """Status info — MDIR style."""

    BORDER_TITLE = " Status "

    def compose(self) -> ComposeResult:
        yield Label("[#ffff55]Model:[/]  -", id="status-model")
        yield Label("[#ffff55]Agents:[/] 0/3", id="status-agents")
        yield Label("[#ffff55]Tokens:[/] 0", id="status-tokens")
        yield Label("", id="status-info")
        yield Label("[#005555]Marviz v0.1.0[/]", id="status-version")

    def update_model(self, model: str) -> None:
        self.query_one("#status-model", Label).update(
            f"[#ffff55]Model:[/]  {model}"
        )

    def update_tokens(self, count: int) -> None:
        self.query_one("#status-tokens", Label).update(
            f"[#ffff55]Tokens:[/] ~{count}"
        )

    def update_status(self, text: str) -> None:
        self.query_one("#status-info", Label).update(
            f"[#00aaaa]{text}[/]"
        )

    def update_agents(self, active: int, total: int) -> None:
        self.query_one("#status-agents", Label).update(
            f"[#ffff55]Agents:[/] {active}/{total}"
        )
