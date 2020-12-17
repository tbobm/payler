"""Tests for payler.db."""
import pytest

from payler import config
from payler.db import SpoolManager


@pytest.mark.asyncio
async def test_init(event_loop):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    manager = SpoolManager(mongo_url, event_loop)
    assert await manager.is_reachable()
    assert manager.collection_name == SpoolManager.DEFAULT_COLLECTION_NAME


@pytest.mark.asyncio
async def test_store(event_loop, payload):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    manager = SpoolManager(mongo_url, event_loop)
    result = await manager.store_payload(payload)
    assert result is True
