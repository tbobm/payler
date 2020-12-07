"""Tests for payler.db."""
import pytest

from payler import config
from payler.db import SpoolManager


@pytest.mark.asyncio
async def test_init():
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    manager = SpoolManager(mongo_url)
    assert await manager.is_reachable()
    assert manager.collection_name == SpoolManager.DEFAULT_COLLECTION_NAME


@pytest.mark.asyncio
async def test_store(payload):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    manager = SpoolManager(mongo_url)
    result = await manager.store_payload(payload)
    assert result is True
