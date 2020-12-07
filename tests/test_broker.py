"""Tests for payler.broker."""
import pytest

from payler import config
from payler.broker import BrokerManager


@pytest.mark.asyncio
async def test_init():
    """Ensure the BrokerManager connects to RabbitMQ."""
    broker_url = config.get('BROKER_URL')
    manager = await BrokerManager.create(broker_url)
    assert await manager.is_reachable()
    # assert manager.collection_name == SpoolManager.DEFAULT_COLLECTION_NAME
