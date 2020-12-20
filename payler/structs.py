"""Common structures and dataclasses."""
from datetime import datetime
import json

from typing import Any
from dataclasses import dataclass, asdict

import msgpack


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

    def message_as_amqp_job(self) -> bytes:
        """Format the payload for amqp processing."""
        if isinstance(self.message, dict):
            return json.dumps(self.message).encode()
        return self.message

    def message_to_bytes(self) -> bytes:
        """Encode message using msgpack."""
        return msgpack.packb(self.message, use_bin_type=True)
