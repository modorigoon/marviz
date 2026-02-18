from textual.message import Message


class UserMessage(Message):
    """User sent a chat message."""

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text


class SubAgentSpawned(Message):
    """A sub-agent was created."""

    def __init__(self, agent_id: str, name: str) -> None:
        super().__init__()
        self.agent_id = agent_id
        self.name = name


class SubAgentCompleted(Message):
    """A sub-agent finished its task."""

    def __init__(self, agent_id: str) -> None:
        super().__init__()
        self.agent_id = agent_id
