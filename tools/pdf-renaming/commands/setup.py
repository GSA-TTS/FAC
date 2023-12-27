import click
import logging
from .tables import (
    Renaming,
    Audit,
    Ims,
    setup_database
    )

logger = logging.getLogger(__name__)

@click.command()
@click.argument('db_filename')
def setup(db_filename):
    setup_database(db_filename)
    Renaming().create_table()
    Audit().create_table()
    Ims().create_table()

