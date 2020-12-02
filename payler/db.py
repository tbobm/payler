"""Database-related utilities."""
import sqlalchemy as sa

from payler.store import Base
from payler import conf


def get_engine(url: str = None):
    """Create the SQLAlchemy Engine."""
    db_url = url
    if url is None:
        db_url = conf.get('DATABASE_URL')
    engine = sa.create_engine(db_url)
    return engine


def get_sessionmaker(engine: sa.engine.Engine) -> sa.orm.sessionmaker:
    """Get a SQL Alchemy sessionmaker instance."""
    maker = sa.orm.sessionmaker()
    maker.configure(bind=engine)
    return maker


def create_structure(engine):
    """Create the tables for database classes."""
    Base.metadata.create_all(engine)
