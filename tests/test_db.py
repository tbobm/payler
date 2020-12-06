"""Tests for payler.db."""
import pytest

from payler.db import SpoolManager


@pytest.mark.asyncio
async def test_init(mongo_url):
    """Ensure the SpoolManager connects to Mongo."""
    manager = SpoolManager(mongo_url)
    assert await manager.is_reachable()
    assert manager.collection_name == SpoolManager.DEFAULT_COLLECTION_NAME


@pytest.mark.asyncio
async def test_store(mongo_url, payload):
    """Ensure the SpoolManager connects to Mongo."""
    manager = SpoolManager('mongodb://payler:secret@localhost/payloads?authSource=admin')
    result = await manager.store_payload(payload)
    assert result is True
