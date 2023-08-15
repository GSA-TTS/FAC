import argparse
from collections import defaultdict
import os
from pathlib import Path
import pandas as pd
import sqlalchemy
from django.db import connection

import csv

from django.core.management.base import BaseCommand

from django.core.files.storage import default_storage
import io

import logging

parser = argparse.ArgumentParser()
dtypes: defaultdict = defaultdict(lambda: str)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.WARNING)


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
            file_bytes = file.read()
            file.close()
            df = pd.read_csv(
                io.BytesIO(file_bytes),
                delimiter="|",
                dtype=dtypes,
                on_bad_lines="skip",
                engine="python",
                quoting=csv.QUOTE_NONE,
                encoding="utf-8",
            )
            df.to_sql(name=make_tablename(txtfile), con=engine)
