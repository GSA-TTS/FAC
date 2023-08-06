import argparse
from collections import defaultdict
import glob
import os
from pathlib import Path
import pandas as pd
import tempfile
import zipfile
import sys
import sqlalchemy 

from django.db import connection

parser = argparse.ArgumentParser()
dtypes = defaultdict(lambda: str)

from django.core.management.base import BaseCommand
from django.conf import settings

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
   
    def add_arguments(self, parser):
        parser.add_argument('zip', type=str)

    def handle(self, *args, **options):
        if "zip" not in options:
            print("One argument (Census full-year pipe-delim zipfile) required.")
            sys.exit()
        # Pandas only places with sqlalchemy engine objects
        engine = sqlalchemy.create_engine(os.getenv("DATABASE_URL").replace("postgres", "postgresql", 1))
        # Do everything in a temp dir.
        # It will disappear when we hit the end of the with block.
        with tempfile.TemporaryDirectory('_fac') as tdir:
            # https://stackoverflow.com/questions/3451111/unzipping-files-in-python
            with zipfile.ZipFile(options["zip"], 'r') as zip_ref:
                zip_ref.extractall(tdir)
            for filename in glob.glob(os.path.join(tdir, '*.txt')):
                print(f'{filename}')
                # Census exports data in CP-1252.
                df = pd.read_csv(filename, delimiter="|", encoding='cp1252', dtype=dtypes)
                # https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
                tablename = Path(filename).stem
                # tablename = re.sub(r"[0-9]+", "", tablename)
                df.to_sql(name=f'census_{tablename}', con=engine)
