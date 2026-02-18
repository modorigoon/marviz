from textual.widgets import Static


class TitleBar(Static):
    """MDIR-style title bar at the top."""

    DEFAULT_CSS = """
    TitleBar {
        dock: top;
        height: 1;
        background: black;
        color: #aaaaaa;
        text-align: center;
    }
    """

    def __init__(self) -> None:
        super().__init__(
            " MARVIZ 0.1 \u2500 Terminal AI Dev Environment ",
            id="title-bar",
        )
