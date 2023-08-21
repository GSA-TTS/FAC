import argparse
from collections import defaultdict
import os
from pathlib import Path
import pandas as pd
import sqlalchemy
from django.db import connection
from django.core.management.base import BaseCommand
import logging
import csv
from django.core.files.storage import default_storage
import io

parser = argparse.ArgumentParser()
dtypes: defaultdict = defaultdict(lambda: str)


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for logger in loggers:
    logger.setLevel(logging.WARNING)


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
        logger.warning(f"engine created {engine}")
        (_, files) = default_storage.listdir(options["path"])
        if not files or len(files) == 0:
            logger.warning("No files to load")
            return

        for txtfile in files:
            with connection.cursor() as cursor:
                cursor.execute(f"DROP TABLE IF EXISTS {make_tablename(txtfile)}")

        for txtfile in files:
            file = default_storage.open(f"{options['path']}/{txtfile}", "rb")
            file_bytes = file.read()  # .decode('utf-8', 'replace')
            file.close()
            df = pd.read_csv(
                io.BytesIO(file_bytes),  # .encode('utf-8', 'skip')),
                delimiter="|",
                dtype=dtypes,
                # low_memory=False,
                on_bad_lines="skip",
                engine="python",
                quoting=csv.QUOTE_NONE,
                # lineterminator='\n',
                encoding="utf-8",
            )
            df.to_sql(name=make_tablename(txtfile), con=engine)
            logger.warning(f"Loaded {make_tablename(txtfile)}")

        GEN_QUERY = """
            SELECT
                count(*)
            FROM
                census_gen19
        """
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text(GEN_QUERY))
            print("Gen table has:", result.all())
