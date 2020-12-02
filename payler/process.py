"""Main application functions."""
import sqlalchemy as sa
from payler import config
from payler import db


def init_db(database_url: str) -> sa.engine.Engine:
    """Set up the Database and create an Engine."""
    engine = db.get_engine(database_url)
    db.create_structure(engine)
    return engine


def setup_app():
    """Configure the application services."""
    database_url = config.get('MONGODB_URL')
    init_db(database_url)
