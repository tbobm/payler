"""CLI entrypoints."""
import asyncio

from payler.broker import BrokerManager
from payler import config
from payler.db import SpoolManager

from payler import process


async def main(loop):
    """Start Payler using the CLI flags."""
    broker_url = config.get('BROKER_URL')
    mongo_url = config.get('MONGODB_URL')
    storage_manager = SpoolManager(mongo_url, loop=loop)
    print(await storage_manager.is_reachable())
    broker_manager = await BrokerManager.create(broker_url, loop=loop)
    broker_manager.configure(
        action=process.spool_message,
        driver=storage_manager,
    )  # action=print, driver=None
    await broker_manager.serve()


def run_cli():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()


if __name__ == "__main__":
    run_cli()
