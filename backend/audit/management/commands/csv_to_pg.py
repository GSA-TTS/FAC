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

from django.core.files.storage import default_storage
import io

# This assumes that the file
#
# allfac22.zip
#
# Is in the private S3 bucket at the location
#
# /fixture-data/allfac22.zip


def make_tablename(filename):
    return "census_" + Path(filename).stem


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, required=True)

    def handle(self, *args, **options):
        engine = sqlalchemy.create_engine(
            os.getenv("DATABASE_URL").replace("postgres", "postgresql", 1)
        )
        (_, files) = default_storage.listdir(options["path"])

        for txtfile in files:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {make_tablename(txtfile)}")

        for txtfile in files:
            file = default_storage.open(f"{options['path']}/{txtfile}", "rb")
            file_bytes = io.BytesIO(file.read())
            file.close()
            # Because the files were encoded in CP1252, we have to wrap them in that
            # encoding to pull them apart in Pandas correctly.
            wrapped = io.TextIOWrapper(
                file_bytes, encoding="cp1252", line_buffering=True
            )
            # Census exports data in CP-1252.
            df = pd.read_csv(wrapped, delimiter="|", encoding="cp1252", dtype=dtypes)
            df.to_sql(name=make_tablename(txtfile), con=engine)
