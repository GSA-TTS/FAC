import json
import click
import logging
from types import SimpleNamespace
from .tables import (
    create_table_from_template,
    load_table_from_template,
    setup_database
)

logger = logging.getLogger(__name__)


def load_ims(ims_filename, audit_filename):
    # https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object
    ims_obj = json.load(open(ims_filename, "r"), object_hook=lambda d: SimpleNamespace(**d))
    audit_obj = json.load(open(audit_filename, "r"), object_hook=lambda d: SimpleNamespace(**d))
    logger.info(f"IMS LENGTH   {len(ims_obj.ELECAUDITHEADER_IMS)}")
    logger.info(f"AUDIT LENGTH {len(audit_obj.ELECAUDITHEADER)}")
    return ims_obj, audit_obj

@click.command()
@click.argument("db_filename")
@click.argument("ims_filename")
@click.argument("audit_filename")
def load(db_filename, ims_filename, audit_filename):
    setup_database(db_filename)
    create_table_from_template("ims", db_filename)
    create_table_from_template("audit", db_filename)
    ims_obj, audit_obj = load_ims(ims_filename, audit_filename)
    load_table_from_template("ims", db_filename, ims_obj.ELECAUDITHEADER_IMS)
    load_table_from_template("audit", db_filename, audit_obj.ELECAUDITHEADER)
