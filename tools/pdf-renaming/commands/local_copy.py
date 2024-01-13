import click
import logging
import os
import time
from .tables import (
    Renaming,
    setup_database,
    setup_postgres_database
    )
from .constants import *
from .s3_support import s3_copy
import multiprocessing as mp

logger = logging.getLogger(__name__)

def timing_update(t0, limit):
    t1 = time.time()
    print({
        "delta": (t1-t0),
        "each": (t1-t0)/float(limit),
        "count": limit
    })

# https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# result_q = mp.Queue()

def process_list_of_objects(argd):
    obj_ls = argd["obj_ls"]
    destination_path = argd["destination_path"]
    live_run = argd["live_run"]

    t0 = time.time()
    ticker = 0

    result_list = []
    r: Renaming
    for r in obj_ls:
        ticker += 1
        if ticker % 100 == 0:
            timing_update(t0, ticker)
        dest_file = os.path.join(destination_path, r.gsa_name)

        if live_run:
            is_good = s3_copy({
                "local_temp_path": destination_path,
                "source_env": "census",
                "source_file": f"{r.census_path}{r.census_name}", 
                "destination_env": "local",
                "destination_file": dest_file
                },
                live_run)
            if is_good:
                r.gsa_file_copied = True
            else: 
                r.gsa_file_copied = False
            r.save()
            # result_list.append(r)
    # result_q.put(result_list)

@click.command()
@click.option('--destination_path', default="local")
@click.option('-l', '--limit', default=None)
@click.option('-y', '--year', default=2022)
@click.option("-r", "--live_run", default=False)
@click.option('-p', '--parallel', default=0)
def local_copy( 
        destination_path,
        limit, year, live_run,
        parallel):
    # Just in case
    parallel = int(parallel)

    print("Setting up the Postgres DB")    
    setup_postgres_database()

    print("Building the lazy query")
    q = (Renaming.select()
         .where(Renaming.census_file_exists == 1, 
                Renaming.year == int(year), 
                # Only copy files we have not previously attempted to copy.
                Renaming.gsa_file_copied.is_null()))

    if limit:
        print(f"Set query limit to {limit}")
        q = q.limit(int(limit))

    if parallel == 0:
        print("No parallelism selected.")
        objects = list(q)
        argd = {
            "obj_ls": objects,
            "destination_path": destination_path,
            "live_run": live_run,
        }
        # process_list_of_objects puts a list of results on the queue
        process_list_of_objects(argd)
        # for o in result_q.get():
        #     o.save()
    else:
        print("Getting renaming objects from DB")
        time.sleep(1)
        objects = list(q)
        print("Chunking")
        object_lists = list(chunks(objects, parallel))
        print("Constructing argument dictionaries")
        argds = list(map(lambda ls: {
            "obj_ls": ls,
            "destination_path": destination_path,
            "live_run": live_run,
        }, object_lists))
        print("Building process list")
        processes = [mp.Process(target=process_list_of_objects, args=(argd,)) for argd in argds]
        print("Running processes")
        # Run processes
        for p in processes:
            p.start()

        # Exit the completed processes
        for p in processes:
            p.join()
        
        # for _ in processes:
        #     objects_to_save = result_q.get()
        #     for o in objects_to_save:
        #         o.save()
