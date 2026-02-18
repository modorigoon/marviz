from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Input, RichLog


class ChatPanel(Vertical):
    """Main agent chat panel — MDIR style."""

    BORDER_TITLE = " Main Agent "

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, id="chat-log")
        yield Input(placeholder="> ", id="chat-input")

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write("[b white]MARVIZ[/] AI Development Environment")
        log.write("[#00aaaa]Ready. Type a message to begin.[/]")
        log.write("")
