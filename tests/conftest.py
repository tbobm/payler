"""Pytest configuration for unit testing."""
from datetime import datetime, timedelta
import json

import pytest

from payler import structs


@pytest.fixture
def time_1():
    """Reference time."""
    now = datetime.now()
    return now


@pytest.fixture
def base_payload(time_1):
    payload = {
        'message': 'sampletest hey',
        'ID': 332,
    }
    return json.dumps(payload).encode()


@pytest.fixture
def payload(base_payload, time_1):
    return structs.Payload(
        base_payload,
        time_1 + timedelta(seconds=5),
        'source_queue',
        'destination_queue',
    )
