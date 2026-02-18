from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, RichLog


class TerminalPanel(Vertical):
    """Terminal — MDIR style."""

    BORDER_TITLE = " Terminal "

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id="terminal-log")
        yield Input(placeholder="$ ", id="terminal-input")

    def on_mount(self) -> None:
        log = self.query_one("#terminal-log", RichLog)
        log.write("[#55ff55]$[/] [#005555]ready[/]")
