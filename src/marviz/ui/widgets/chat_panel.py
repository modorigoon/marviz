from textual.app import ComposeResult
from textual.containers import Vertical
from textual.events import Key
from textual.widgets import RichLog, Static, TextArea

from ..messages import UserMessage


class ChatInput(TextArea):
    """Chat input with Enter-to-submit, Shift+Enter for newline."""

    def _on_key(self, event: Key) -> None:
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            text = self.text.strip()
            if text:
                self.clear()
                self.post_message(UserMessage(text))
            return
        super()._on_key(event)


class ChatPanel(Vertical):
    """Main agent chat panel — MDIR style."""

    BORDER_TITLE = " Main Agent "

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._response_buffer = ""

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, wrap=True, min_width=0, id="chat-log")
        yield Static("", id="chat-streaming")
        yield ChatInput(id="chat-input", placeholder="> Message...")

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write("[b white]MARVIZ[/] AI Development Environment")
        log.write("[#00aaaa]Ready. Type a message to begin.[/]")
        log.write("")

    def show_user_message(self, text: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(f"[b #ffff55]> {text}[/]")

    def append_token(self, text: str) -> None:
        """Append a streaming token — renders in real-time via Static."""
        self._response_buffer += text
        streaming = self.query_one("#chat-streaming", Static)
        streaming.update(self._response_buffer)

    def show_error(self, text: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        log.write(f"[b red]Error:[/] {text}")

    def finish_response(self) -> None:
        """Move buffered response into the RichLog and reset."""
        if self._response_buffer:
            log = self.query_one("#chat-log", RichLog)
            log.write(self._response_buffer)
        self._response_buffer = ""
        streaming = self.query_one("#chat-streaming", Static)
        streaming.update("")
