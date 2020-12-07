"""Pytest configuration for unit testing."""
import os
from datetime import datetime, timedelta

import pytest

from payler import structs


@pytest.fixture
def time_1():
    """Reference time."""
    now = datetime.now()
    return now


@pytest.fixture
def base_payload(time_1):
    return {
        'message': 'sampletest hey',
        'ID': 332,
        'date': time_1,
    }


@pytest.fixture
def payload(base_payload, time_1):
    return structs.Payload(
        base_payload,
        time_1 + timedelta(seconds=5),
        'source_queue',
        'destination_queue',
    )
