"""CLI entrypoints."""
import asyncio

import click

from payler import config, logs, runtime
from payler.broker import BrokerManager
from payler.db import SpoolManager

from payler import process


async def process_queue(loop: asyncio.events.AbstractEventLoop):
    """Start Payler using the CLI flags."""
    broker_url = config.get('BROKER_URL')
    mongo_url = config.get('MONGODB_URL')
    storage_manager = SpoolManager(mongo_url, loop=loop)
    await storage_manager.is_reachable()
    broker_manager = await BrokerManager.create(broker_url, loop=loop)
    broker_manager.configure(
        action=process.spool_message,
        driver=storage_manager,
    )  # action=print, driver=None
    await broker_manager.serve()


async def watch_storage(loop: asyncio.events.AbstractEventLoop):
    """Watch the storage and inject in BrokerManager exchange."""
    logger = logs.build_logger('watch_storage')
    broker_url = config.get('BROKER_URL')
    mongo_url = config.get('MONGODB_URL')
    storage_manager = SpoolManager(mongo_url, loop=loop, logger=logger)
    await storage_manager.is_reachable()
    broker_manager = await BrokerManager.create(broker_url, loop=loop)
    logger.info(
        'configuring SpoolManager with action=%s driver=%s',
        'process.send_message_back',
        'BrokerManager',
    )
    storage_manager.configure(
        action=process.send_message_back,
        driver=broker_manager,
    )  # action=print, driver=None
    await storage_manager.search_ready()


def listen_to_broker():
    """Watch the payload queue for payload to delay."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_queue(loop))
    loop.close()


def watch_payloads_ready():
    """Watch the Storage and re-inject matured payloads."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(watch_storage(loop))
    loop.close()


@click.command()
@click.option(
    '--config-file',
    help='Payler configuration file.',
    type=click.File('r'),
    required=True,
)
def run_payler(config_file):
    """Register workflows and start processing."""
    configuration = config.load(config_file)
    loop = asyncio.get_event_loop()
    workflows = runtime.register_workflows(
        configuration['workflows'],
        loop,
    )
    for workflow in workflows:
        workflow.register_action()
    loop.run_forever()

if __name__ == "__main__":
    listen_to_broker()
