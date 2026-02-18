from pathlib import Path

from textual.app import App

from .ui.screens.main_screen import MainScreen

CSS_PATH = Path(__file__).parent / "ui" / "styles" / "app.tcss"


class MarvizApp(App):
    """Marviz - MDIR-style Terminal AI Dev Environment."""

    TITLE = "Marviz"
    CSS_PATH = CSS_PATH
    SCREENS = {"main": MainScreen}

    def on_mount(self) -> None:
        self.push_screen("main")
