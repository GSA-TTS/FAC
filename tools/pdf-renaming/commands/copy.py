import click
import logging
import time
from playhouse.shortcuts import model_to_dict
from .tables import (
    Renaming,
    setup_database
    )
from .constants import *
from .s3_support import s3_copy, s3_check_exists

logger = logging.getLogger(__name__)

def timing_update(t0, limit):
    t1 = time.time()
    print({
        "delta": (t1-t0),
        "each": (t1-t0)/float(limit),
        "count": limit
    })

@click.command()
@click.argument("db_filename")
@click.argument("local_temp_path")
@click.option('-l', '--limit', default=None)
@click.option('-y', '--year', default=2022)
@click.option("-r", "--live_run", default=False)
def copy(db_filename, local_temp_path, limit, year, live_run):
    setup_database(db_filename)
    t0 = time.time()
    ticker = 0

    q = (Renaming.select()
         .where(Renaming.census_file_exists == True, 
                Renaming.year == int(year), 
                # Only copy files we have not previously copied.
                Renaming.gsa_file_copied.is_null()))

    if limit:
        print(f"Set query limit to {limit}")
        q = q.limit(int(limit))

    r: Renaming
    for r in q.iterator():
        dest_file = f"{r.gsa_path}{r.gsa_name}"
        s3_copy({
            "local_temp_path": local_temp_path,
            "source_env": "census",
            "source_file": f"{r.census_path}{r.census_name}", 
            "destination_env": "preview",
            "destination": dest_file
            },
            live_run)
        if live_run:
            is_copied = s3_check_exists("preview", dest_file)
            # If it doesn't copy, record it.
            if not is_copied:
                print(f"Copy failed: {dest_file}")
            r.gsa_file_copied = is_copied
            r.save()
