import click
import logging
import os
from botocore.client import ClientError
from types import SimpleNamespace
from .tables import (
    Renaming,
    setup_database
    )
import time
from .s3_support import get_s3_client

logger = logging.getLogger(__name__)


def timing_update(t0, limit):
    t1 = time.time()
    print({
        "delta": (t1-t0),
        "each": (t1-t0)/float(limit),
        "count": limit
    })


@click.command()
@click.argument('db_filename')
@click.option('-l', '--limit', default=None)
@click.option('-y', '--year', default=2022)
def check(db_filename, limit, year):
    setup_database(db_filename)

    s3 = get_s3_client("census")
    bucket_name = os.getenv("CENSUS_BUCKET_NAME")

    q = (Renaming
         .select()
         .where(Renaming.census_file_exists.is_null())
         .where(Renaming.gsa_name.startswith(str(year)) )
         )
    if limit:
        print(f"Set query limit to {limit}")
        q = q.limit(int(limit))

    t0 = time.time()
    ticker = 0

    for r in q:
        ticker += 1
        if (ticker % 1000) == 0:
            timing_update(t0, ticker)

        key = r.census_path + r.census_name

        try:
            ho = s3.head_object(
                Bucket = bucket_name,
                Key = key
            )
            r.census_file_exists = 1
            r.save()
        except ClientError as ce:
            r.census_file_exists = 0
            r.save()
    
    print("Done.")
    timing_update(t0, ticker)
