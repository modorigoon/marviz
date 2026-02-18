from __future__ import annotations

from pathlib import Path

from rich.style import Style
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import TextArea
from textual.widgets.text_area import TextAreaTheme

_MDIR_THEME = TextAreaTheme(
    name="mdir",
    base_style=Style(color="#aaaaaa", bgcolor="#000080"),
    gutter_style=Style(color="#005555", bgcolor="#000080"),
    cursor_style=Style(color="#000080", bgcolor="#55ffff"),
    cursor_line_style=Style(bgcolor="#000060"),
    cursor_line_gutter_style=Style(color="#00aaaa", bgcolor="#000060", bold=True),
    bracket_matching_style=Style(color="#ffff55", bold=True),
    selection_style=Style(bgcolor="#003060"),
    syntax_styles={
        "string": Style(color="#55ff55"),
        "string.documentation": Style(color="#55ff55"),
        "comment": Style(color="#005555", italic=True),
        "keyword": Style(color="#55ffff", bold=True),
        "operator": Style(color="#00aaaa"),
        "conditional": Style(color="#55ffff"),
        "number": Style(color="#ff5555"),
        "float": Style(color="#ff5555"),
        "function": Style(color="#ffff55"),
        "function.call": Style(color="#ffff55"),
        "method": Style(color="#ffff55"),
        "method.call": Style(color="#ffff55"),
        "boolean": Style(color="#ff5555"),
        "class": Style(color="#55ffff", bold=True),
        "type": Style(color="#55ffff"),
        "regex": Style(color="#ff5555"),
        "escape": Style(color="#ff5555"),
        "heading": Style(color="#ffff55", bold=True),
        "tag": Style(color="#55ffff"),
        "attribute": Style(color="#ffff55"),
    },
)

_EXT_TO_LANGUAGE: dict[str, str | None] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".md": "markdown",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".rs": "rust",
    ".go": "go",
    ".sh": "bash",
    ".bash": "bash",
    ".sql": "sql",
    ".xml": "xml",
}


class CodeEditorPanel(Vertical):
    """Code editor — MDIR style."""

    BORDER_TITLE = " Editor "

    def compose(self) -> ComposeResult:
        yield TextArea(
            "",
            id="code-editor",
            show_line_numbers=True,
            read_only=True,
        )

    def on_mount(self) -> None:
        editor = self.query_one("#code-editor", TextArea)
        editor.register_theme(_MDIR_THEME)
        editor.theme = "mdir"

    def open_file(self, path: Path) -> None:
        """Load a file into the editor."""
        editor = self.query_one("#code-editor", TextArea)
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            try:
                content = path.read_text(encoding="latin-1")
            except Exception as e:
                content = f"(Cannot read file: {e})"

        lang = _EXT_TO_LANGUAGE.get(path.suffix.lower())
        editor.language = lang
        editor.load_text(content)
        self.border_title = f" {path.name} "
