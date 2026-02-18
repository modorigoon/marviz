from textual.widgets import RichLog


class AgentPanel(RichLog):
    """Single sub-agent output panel — MDIR style."""

    def __init__(self, agent_name: str = "Sub-Agent", **kwargs) -> None:
        super().__init__(highlight=True, markup=True, **kwargs)
        self._agent_name = agent_name

    def on_mount(self) -> None:
        self.write(f"[#005555]{self._agent_name} \u2500 idle[/]")
