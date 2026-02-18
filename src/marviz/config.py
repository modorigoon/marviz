import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class MarvizConfig:
    """Application configuration loaded from environment."""

    default_model: str = "claude-sonnet-4-20250514"
    max_sub_agents: int = 3
    working_dir: Path = field(default_factory=Path.cwd)

    @classmethod
    def load(cls) -> "MarvizConfig":
        load_dotenv()
        return cls(
            default_model=os.getenv("MARVIZ_DEFAULT_MODEL", cls.default_model),
            max_sub_agents=int(os.getenv("MARVIZ_MAX_SUB_AGENTS", str(cls.max_sub_agents))),
        )
