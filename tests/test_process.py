"""Test configuration management module."""
import pendulum
import pymongo
import pytest
from aio_pika import Message

from payler import config, process
from payler.db import SpoolManager
from payler.driver import DriverConfiguration


@pytest.mark.asyncio
async def test_spool_message(event_loop, monkeypatch):
    """Test accessing from constant when set."""
    body = b'data'
    delay =  '10000'
    message = Message(body, headers={'x-delay': delay})
    mongo_url = config.get('MONGODB_URL')
    database = pymongo.MongoClient(mongo_url).get_default_database()
    driver_config = DriverConfiguration(
        'test',
        mongo_url,
        event_loop,
        None,
    )
    manager = SpoolManager(driver_config)
    await manager.is_reachable()

    now = pendulum.now()
    def mockreturn():
        return now

    monkeypatch.setattr(pendulum, 'now', mockreturn)
    result = await process.spool_message(message, manager)
    doc = database[manager.DEFAULTS.get('spool_collection')].find_one(
        {'_id': result.data.inserted_id},
    )
    assert doc is not None
    assert doc['message'] == body

    ref = result.payload.reference_date
    expected_ref = now.add(microseconds=int(delay) * 1_000)
    assert ref == expected_ref
