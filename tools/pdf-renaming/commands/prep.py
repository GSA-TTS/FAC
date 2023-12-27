import click
import logging
import time
from .tables import (
    Renaming, 
    Ims, 
    Audit,
    database_proxy,
    setup_database
    )
from .constants import *

logger = logging.getLogger(__name__)

def get_month(audityear, dbkey):
    obj = Audit.get(Audit.audityear==audityear, Audit.dbkey==dbkey)
    return obj.fyenddate.split("-")[1]

def timing_update(t0, limit):
    t1 = time.time()
    print({
        "delta": (t1-t0),
        "each": (t1-t0)/float(limit),
        "count": limit
    })

@click.command()
@click.argument("db_filename")
def prep(db_filename):
    setup_database(db_filename)

    t0 = time.time()
    ticker = 0

    # To make this go fast, build the structure first.
    page = 0
    turning_pages = True
    while turning_pages:
        to_insert = list()
        q = Ims.select(Ims.audityear, Ims.dbkey, Ims.id2, Ims.version).paginate(page, 10000)
        for ims in q.iterator():
            ticker += 1
            if (ticker % 1000) == 0:
                timing_update(t0, ticker)
            renamed = f"{ims.audityear}-{get_month(ims.audityear, ims.dbkey)}-CENSUS-{str(ims.dbkey).zfill(10)}"
            to_insert.append({
                "year": ims.audityear,
                "id2": ims.id2,
                "version": ims.version,
                "census_path": CENSUS_PATH,
                "census_name": f"{ims.id2}.pdf",
                "gsa_path": GSA_PATH,
                "gsa_name": renamed,
            })
        if to_insert == []:
            break
        else:
            print("Inserting many...")
            Renaming.insert_many(to_insert).execute()
            page += 1
