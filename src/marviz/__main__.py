"""Entry point for python -m marviz."""

from .app import MarvizApp


def main() -> None:
    app = MarvizApp()
    app.run()


if __name__ == "__main__":
    main()
