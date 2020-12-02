"""Click subcommands to manage payler."""
from io import TextIOWrapper

import click

from payler import transfer, db
from payler.store import store_workflow


@click.command('import')
@click.argument('filename', type=click.File('r'))
def import_yaml(filename: TextIOWrapper):
    """Load a YAML in DB."""
    workflow = transfer.import_workflow_from_yaml(filename)
    engine = db.get_engine()
    sessionmaker = db.get_sessionmaker(engine)
    store_workflow(sessionmaker, workflow)
