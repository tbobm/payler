"""Common structures and dataclasses."""
from datetime import datetime
from typing import Any
from dataclasses import dataclass, asdict


@dataclass
class Payload:
    """Wrapper around the actual payload.

    Wrap the payload content and provide metadata for payler.

    message: Original payload  # NOTE: could be pickled
    reup_time: Date after which the payload should be sent to the output queue.
    source: Queue from which the payload originated
    destination: Queue to which the payload should be sent back
    """
    message: Any
    reference_date: datetime
    source: str
    destination: str

    def asdict(self) -> dict:
        """Return a the Payload using a dictionary representation."""
        return asdict(self)
