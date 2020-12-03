"""Database-related utilities."""
import motor


class SpoolManager:
    """Interface to store payloads and interact with the Database."""

    def __init__(self, url: str = None):
        # TODO: Add logger
        """Create the backend connection."""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.client.ping()
