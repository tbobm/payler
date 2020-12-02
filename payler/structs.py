"""Common structures and dataclasses."""
from datetime import timedelta
import typing
from dataclasses import dataclass, field


@dataclass
class Payload:
    """Answer related to a Question."""
    title: str
    score: int = 0
