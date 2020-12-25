"""Tests for payler.db."""
import datetime

import pendulum
import pytest
import pymongo

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
async def test_setup(event_loop):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    manager = SpoolManager(mongo_url, event_loop)
    assert await manager.is_reachable()

    index_name = await manager.setup()
    infos = await manager.collection.index_information()
    assert index_name in infos

    created = await manager.setup()
    await manager.collection.drop_index(index_name)

@pytest.mark.asyncio
async def test_store(event_loop, payload):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    manager = SpoolManager(mongo_url, event_loop)
    result = await manager.store_payload(payload)
    assert result is not None

    doc = await manager.collection.find_one({'_id': result.inserted_id})
    assert doc is not None
    await manager.collection.delete_one({'_id': doc['_id']})


@pytest.mark.asyncio
async def test_search_ready(event_loop, payload):
    """Ensure the SpoolManager connects to Mongo."""
    mongo_url = config.get('MONGODB_URL')
    manager = SpoolManager(mongo_url, event_loop)
    payload1 = payload
    date_1 = pendulum.now().subtract(minutes=2)
    payload1.reference_date = date_1
    result1 = await manager.store_payload(payload1)
    assert result1 is not None
    payload2 = payload
    date_2 = pendulum.now().subtract(minutes=2)
    payload2.reference_date = date_2
    result2 = await manager.store_payload(payload2)
    assert result2 is not None

    async def delete_document(document, driver):
        collection = driver.client.get_default_database()[driver.DEFAULT_COLLECTION_NAME]
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
    count = database[manager.DEFAULT_COLLECTION_NAME].count_documents({
        '_id': {
            '$in': [
                result1.inserted_id,
                result2.inserted_id,
            ],
        },
        'found': True,

    })
    assert count == 0
