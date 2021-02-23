"""Tests for payler.db."""
import datetime

import pendulum
import pytest
import pymongo

from payler import config
from payler.db import SpoolManager
from payler.driver import DriverConfiguration


@pytest.mark.asyncio
async def test_init(event_loop):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    driver_config = DriverConfiguration(
        'test',
        mongo_url,
        event_loop,
        None,
    )
    manager = SpoolManager(driver_config)
    assert await manager.is_reachable()


@pytest.mark.asyncio
async def test_setup(event_loop):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    driver_config = DriverConfiguration(
        'test',
        mongo_url,
        event_loop,
        None,
    )
    manager = SpoolManager(driver_config)
    assert await manager.is_reachable()

    index_name = await manager.setup()
    infos = await manager.collection.index_information()
    assert index_name in infos

    _ = await manager.setup()
    await manager.collection.drop_index(index_name)


@pytest.mark.asyncio
async def test_process(event_loop, payload):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    driver_config = DriverConfiguration(
        'test',
        mongo_url,
        event_loop,
        None,
    )
    manager = SpoolManager(driver_config)
    result = await manager.process(payload)
    assert result is not None

    doc = await manager.collection.find_one({'_id': result.data.inserted_id})
    assert doc is not None
    await manager.collection.delete_one({'_id': doc['_id']})


@pytest.mark.asyncio
async def test_search_ready(event_loop, payload):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    driver_config = DriverConfiguration(
        'test',
        mongo_url,
        event_loop,
        None,
    )
    manager = SpoolManager(driver_config)
    payload1 = payload
    date_1 = pendulum.now().subtract(minutes=2)
    payload1.reference_date = date_1
    result1 = await manager.process(payload1)
    assert result1 is not None
    payload2 = payload
    date_2 = pendulum.now().subtract(minutes=2)
    payload2.reference_date = date_2
    result2 = await manager.process(payload2)
    assert result2 is not None

    async def delete_document(document, driver):
        name = driver.DEFAULTS.get('spool_collection')
        collection = driver.client.get_default_database()[name]
        await collection.update_one(
            {'_id': document['_id']},
            { '$set': {
                    'found': "12"
                }
            }
        )

    manager.configure(delete_document, driver=manager)

    await manager.process_and_cleanup()

    database = pymongo.MongoClient(mongo_url).get_default_database()
    count = database[manager.DEFAULTS.get('spool_collection')].count_documents({
        '_id': {
            '$in': [
                result1.data.inserted_id,
                result2.data.inserted_id,
            ],
        },
        'found': True,

    })
    assert count == 0
