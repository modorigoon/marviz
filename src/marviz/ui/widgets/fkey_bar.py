from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label


FKEYS = [
    ("1", "Help"),
    ("2", "Chat"),
    ("3", "View"),
    ("4", "Edit"),
    ("5", "Agnt"),
    ("6", "Modl"),
    ("7", "Term"),
    ("8", "Tree"),
    ("9", "Conf"),
    ("10", "Quit"),
]


class FKeyBar(Horizontal):
    """MDIR-style function key bar."""

    DEFAULT_CSS = """
    FKeyBar {
        dock: bottom;
        height: 1;
        background: black;
    }
    FKeyBar .fkey-num {
        width: auto;
        background: black;
        color: #aaaaaa;
    }
    FKeyBar .fkey-label {
        width: auto;
        background: #00aaaa;
        color: black;
        text-style: bold;
    }
    FKeyBar .fkey-spacer {
        width: 1fr;
        background: black;
    }
    """

    def compose(self) -> ComposeResult:
        for num, label in FKEYS:
            yield Label(num, classes="fkey-num")
            yield Label(f"{label:<4}", classes="fkey-label")
        yield Label("", classes="fkey-spacer")
