from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen

from ..widgets import (
    AgentContainer,
    ChatPanel,
    CodeEditorPanel,
    FileTreePanel,
    FKeyBar,
    StatusBar,
    TerminalPanel,
    TitleBar,
)


class MainScreen(Screen):
    """MDIR-style main screen.

    ╔═══════════╦══════════════════╦═══════════╗
    ║           ║  Worker-1        ║ Files     ║
    ║  Main     ║──────────────────║───────────║
    ║  Agent    ║  Worker-2        ║ Editor    ║
    ║  (Chat)   ║──────────────────║           ║
    ║           ║  Worker-3        ║           ║
    ╠═══════════╩══════════════════╬═══════════╣
    ║  Status                      ║ Terminal  ║
    ╚══════════════════════════════╩═══════════╝
    1Help 2Chat 3View 4Edit 5Agent 6Model 7Term 8Tree 9Conf 10Quit
    """

    BINDINGS = [
        ("f1", "help", "Help"),
        ("f2", "focus_chat", "Chat"),
        ("f7", "focus_terminal", "Term"),
        ("f8", "focus_tree", "Tree"),
        ("f10", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield TitleBar()
        with Vertical(id="app-body"):
            with Horizontal(id="main-area"):
                yield ChatPanel(id="chat-panel")
                yield AgentContainer(id="agent-container")
                with Vertical(id="right-column"):
                    yield FileTreePanel(id="file-tree-panel")
                    yield CodeEditorPanel(id="code-editor-panel")
            with Horizontal(id="bottom-row"):
                yield StatusBar()
                yield TerminalPanel(id="terminal-panel")
        yield FKeyBar()

    def action_focus_chat(self) -> None:
        self.query_one("#chat-input").focus()

    def action_focus_terminal(self) -> None:
        self.query_one("#terminal-input").focus()

    def action_focus_tree(self) -> None:
        self.query_one("#file-tree").focus()

    def action_help(self) -> None:
        log = self.query_one("#chat-log")
        log.write("[#ffff55]F1[/]=Help [#ffff55]F2[/]=Chat [#ffff55]F7[/]=Term [#ffff55]F8[/]=Tree [#ffff55]F10[/]=Quit")
