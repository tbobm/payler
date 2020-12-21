"""Test configuration management module."""
import pendulum
import pymongo
import pytest
from aio_pika import Message

from payler.db import SpoolManager
from payler import config, process


@pytest.mark.asyncio
async def test_spool_message(event_loop, monkeypatch):
    """Test accessing from constant when set."""
    body = b'data'
    delay =  '10000'
    message = Message(body, headers={'x-delay': delay})
    mongo_url = config.get('MONGODB_URL')
    database = pymongo.MongoClient(mongo_url).get_default_database()
    manager = SpoolManager(mongo_url, event_loop)
    await manager.is_reachable()

    now = pendulum.now()
    def mockreturn():
        return now

    monkeypatch.setattr(pendulum, 'now', mockreturn)
    result, payload = await process.spool_message(message, manager)
    doc = database[manager.DEFAULT_COLLECTION_NAME].find_one(
        {'_id': result.inserted_id},
    )
    assert doc is not None
    assert doc['message'] == body

    ref = payload.reference_date
    expected_ref = now.add(microseconds=int(delay) * 1_000)
    assert ref == expected_ref
