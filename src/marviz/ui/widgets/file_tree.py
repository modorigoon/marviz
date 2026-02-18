from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import DirectoryTree


class FileTreePanel(Vertical):
    """File browser — MDIR style."""

    BORDER_TITLE = " Files "

    def compose(self) -> ComposeResult:
        yield DirectoryTree(Path.cwd(), id="file-tree")
