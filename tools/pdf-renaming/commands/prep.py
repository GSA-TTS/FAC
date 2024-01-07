import click
import logging
import time
from peewee import fn
import sys
from playhouse.shortcuts import model_to_dict, dict_to_model

from .tables import (
    Renaming, 
    Ims, 
    Audit,
    database_proxy,
    setup_database
    )
from .constants import *

CHUNKSIZE = 1000

logger = logging.getLogger(__name__)

def get_month(audityear, dbkey):
    try:
        obj = Audit.get(Audit.audityear==audityear, Audit.dbkey==dbkey)
        return obj.fyenddate.split("-")[1]
    except Exception as e:
        return None
    
def timing_update(t0, limit):
    t1 = time.time()
    print({
        "delta": (t1-t0),
        "each": (t1-t0)/float(limit),
        "count": limit
    })

def group_query(q):

    t0 = time.time()
    ticker = 0
    to_insert = list()

    for I in q.iterator():
        # If I can't find it, we're not renaming it.
        ticker += 1
        if ticker % CHUNKSIZE == 0:
            timing_update(t0, ticker)
            print(f"Inserting {len(to_insert)} renamings")
            Renaming.insert_many(to_insert).execute()
            to_insert = list()

        try:
            Ir = (Ims.select()
                .where(Ims.audityear == I.audityear,
                        Ims.dbkey == I.dbkey,
                        )
                .group_by(Ims.version)
                .having(Ims.version == fn.MAX(Ims.version))
                .order_by(Ims.version)
                )
            
            # Grab the highest version object.
            # It will be last, because of the order-by.
            ims = list(Ir)[-1]
            month = get_month(ims.audityear, ims.dbkey)
            if month:
                renamed = f"{ims.audityear}-{month}-CENSUS-{str(ims.dbkey).zfill(10)}.pdf"
                to_insert.append({
                    "year": ims.audityear,
                    "id2": ims.id2,
                    "version": ims.version,
                    "census_path": CENSUS_PATH,
                    "census_name": f"{ims.id2}.pdf",
                    "gsa_path": GSA_PATH,
                    "gsa_name": renamed,
                })
            else:
                print(f"No month found for {ims.audityear}, {ims.dbkey}")
                to_insert.append({
                    "year": ims.audityear,
                    "id2": "0",
                    "version": "-1",
                    "census_path": CENSUS_PATH,
                    "census_name": f"census_not_found.pdf",
                    "gsa_path": GSA_PATH,
                    "gsa_name": "GSA_MIGRATION_NOT_FOUND.pdf",
                })
        except Exception as e:
            print(f"Exception! Skipping {ims.audityear}, {ims.dbkey}")
            print(e)


    print(f"Inserting {len(to_insert)} renamings")
    Renaming.insert_many(to_insert).execute()


@click.command()
@click.argument("db_filename")
def prep(db_filename):
    setup_database(db_filename)

    # Now, do all the ones with a version > 1
    q = (Ims.select(Ims.audityear, Ims.dbkey)
         .where(Ims.audityear << ["2022", "2021", "2020", "2019", "2018"])
         .distinct())
    group_query(q)
    