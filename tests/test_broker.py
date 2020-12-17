"""Tests for payler.broker."""
from datetime import datetime, timedelta
import pytest

from payler import config
from payler.broker import BrokerManager
from payler.structs import Payload


@pytest.mark.asyncio
async def test_init():
    """Ensure the BrokerManager connects to RabbitMQ."""
    broker_url = config.get('BROKER_URL')
    manager = await BrokerManager.create(broker_url)
    assert await manager.is_reachable()


@pytest.mark.asyncio
async def test_store():
    """Ensure the Broker quand send a Payload."""
    reference = datetime.now() + timedelta(seconds=5)
    body = 'sample test'
    payload = Payload(body, reference, 'source', 'example')
    broker_url = config.get('BROKER_URL')
    manager = await BrokerManager.create(broker_url)
    delivered = await manager.send_payload(payload, payload.destination)
    assert delivered is not None
    assert delivered.body == body.encode()


@pytest.mark.asyncio
async def configure():
    """Ensure the BrokerManager connects to RabbitMQ."""
    queue_name = 'test_declare'
    broker_url = config.get('BROKER_URL')
    manager = await BrokerManager.create(broker_url)
    assert await manager.is_reachable()
    # TODO: Add configure test


@pytest.mark.asyncio
async def test_serve(event_loop):
    """Ensure the BrokerManager connects to RabbitMQ."""
    queue_name = 'test_declare'
    broker_url = config.get('BROKER_URL')
    manager = await BrokerManager.create(broker_url, event_loop)
    assert await manager.is_reachable()

    async def get_payload(payload, *args):
        print(args)
        print(payload.body.decode())

    manager.configure(get_payload)
    assert manager.configured is True
