"""Processing functions for broker operations."""
import json

import pymongo
import aio_pika
import pendulum

from payler.broker import BrokerManager
from payler.db import SpoolManager
from payler.errors import ProcessingError
from payler.structs import Payload


async def spool_message(message: aio_pika.Message, driver: SpoolManager, **kwargs):
    """Decode and spool `message` using `driver`."""
    delay = int(message.headers.get('x-delay'))
    destination = message.headers.get('x-destination', 'payler-out')
    data = message.body
    now = pendulum.now()
    reference = now.add(microseconds=delay * 1000)  # switch form us to ms
    # TODO: Variabilize source
    source = 'payler-jobs'
    payload = Payload(
        data,
        reference,
        source,
        destination,
    )
    result = await driver.store_payload(payload)
    # TODO: do correct post-processing logging
    return result, reference


async def send_message_back(document: dict, driver: BrokerManager, **kwargs):
    """Inject the Payload back in the Broker."""
    payload = Payload(
        message=document.get('message'),
        reference_date=document.get('reference_date'),
        source=document.get('source'),
        destination=document.get('destination'),
    )
    return await driver.send_payload(payload, routing_key=payload.destination)
