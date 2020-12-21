"""Unit tests for payler.structs module."""
from dataclasses import asdict
from datetime import timedelta
import uuid

from payler import structs


def test_payload(base_payload, time_1, payload):
    # assert fixture is working
    expected = {
        'source': 'source_queue',
        'destination': 'destination_queue',
        'message': base_payload,
        'reference_date': time_1 + timedelta(seconds=5),
    }
    assert asdict(payload) == expected
