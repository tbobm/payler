"""Tests for payler.broker."""
from datetime import datetime, timedelta
import pytest

from payler import config
from payler.broker import BrokerManager
from payler.driver import DriverConfiguration
from payler.structs import Payload


@pytest.mark.asyncio
async def test_init():
    """Ensure the BrokerManager connects to RabbitMQ."""
    broker_url = config.get('BROKER_URL')
    driver_config = DriverConfiguration(
        'test',
        broker_url,
        None,
        None,
    )
    manager = await BrokerManager.create(driver_config)
    assert await manager.is_reachable()


@pytest.mark.asyncio
async def test_store():
    """Ensure the Broker quand send a Payload."""
    reference = datetime.now() + timedelta(seconds=5)
    body = b'sample test'
    payload = Payload(body, reference, 'source', 'example')
    broker_url = config.get('BROKER_URL')
    driver_config = DriverConfiguration(
        'test',
        broker_url,
        None,
        None,
    )
    manager = await BrokerManager.create(driver_config)
    delivered = await manager.process(
        payload,
        routing_key=payload.destination,
    )
    assert delivered is not None
    assert delivered.data.body == body


@pytest.mark.asyncio
async def configure():
    """Ensure the BrokerManager connects to RabbitMQ."""
    queue_name = 'test_declare'
    broker_url = config.get('BROKER_URL')
    driver_config = DriverConfiguration(
        'test',
        broker_url,
        None,
        None,
    )
    manager = await BrokerManager.create(driver_config)
    assert await manager.is_reachable()
    # TODO: Add configure test


@pytest.mark.asyncio
async def test_serve(event_loop):
    """Ensure the BrokerManager connects to RabbitMQ."""
    queue_name = 'test_declare'
    broker_url = config.get('BROKER_URL')
    driver_config = DriverConfiguration(
        'test',
        broker_url,
        None,
        None,
    )
    manager = await BrokerManager.create(driver_config)
    assert await manager.is_reachable()

    async def get_payload(payload, *args):
        print(args)
        print(payload.body.decode())

    manager.configure(get_payload)
    assert manager.action is not None
