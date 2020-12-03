"""Database-related utilities."""
import motor


class SpoolManager:
    """Interface to store payloads and interact with the Database."""

    def __init__(self, url: str = None):
        # TODO: Add logger
        """Create the backend connection."""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(url)
        self.assert_alive()

    def assert_alive(self) -> bool:
        """Ensure connection integrity."""
        return self.client.ping()

    def store_payload(self) -> int:
        """Store the Payload with corresponding metadatas."""
        self.assert_alive()
        return 0
