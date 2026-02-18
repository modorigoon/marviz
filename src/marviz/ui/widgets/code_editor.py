from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import TextArea


class CodeEditorPanel(Vertical):
    """Code editor — MDIR style."""

    BORDER_TITLE = " Editor "

    def compose(self) -> ComposeResult:
        yield TextArea.code_editor("", language="python", id="code-editor")
