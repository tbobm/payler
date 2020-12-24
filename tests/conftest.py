"""Pytest configuration for unit testing."""
from datetime import datetime, timedelta
import io
import json
from textwrap import dedent

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

@pytest.fixture
def example_config():
    """Basic YAML-readable config file."""
    return io.StringIO(dedent("""
    ---
    name: sample
    workflows:
      - name: 'Consume broker payloads and store'
        callable: "client.process_queue"
      - name: "Poll storage and re-inject in RabbitMQ"
        callable: "client.watch_storage"
    """))
