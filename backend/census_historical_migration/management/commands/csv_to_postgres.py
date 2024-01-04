import logging
import boto3
import pandas as pd
import numpy as np


from io import BytesIO
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps
from collections import defaultdict

logger = logging.getLogger(__name__)

census_to_gsafac_models = list(
    apps.get_app_config("census_historical_migration").get_models()
)
census_to_gsafac_model_names = [m._meta.model_name for m in census_to_gsafac_models]
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
)
census_to_gsafac_bucket_name = settings.AWS_PRIVATE_STORAGE_BUCKET_NAME
DELIMITER = ","


class Command(BaseCommand):
    help = """
        Populate Postgres database from csv files
        Usage:
        manage.py csv_to_postgres --folder <folder_name> --clean <True|False>
    """

    def add_arguments(self, parser):
        parser.add_argument("--folder", help="S3 folder name (required)", type=str)
        parser.add_argument(
            "--clean", help="Clean the data (default: False)", type=bool, default=False
        )
        parser.add_argument(
            "--sample",
            help="Sample the data (default: False)",
            type=bool,
            default=False,
        )
        parser.add_argument("--load")
        parser.add_argument(
            "--chunksize",
            help="Chunk size for processing data (default: 10_000)",
            type=int,
            default=10_000,
        )

    def handle(self, *args, **options):
        if options.get("clean"):
            self.delete_data()
            return
        if options.get("sample"):
            self.sample_data()
            return
        folder = options.get("folder")
        if not folder:
            logger.error("Please specify a folder name")
            return
        chunk_size = options.get("chunksize")
        self.process_csv_files(folder, chunk_size)

    def process_csv_files(self, folder, chunk_size):
        items = self.list_s3_objects(census_to_gsafac_bucket_name, folder)
        for item in items:
            if item["Key"].endswith("/"):
                continue
            model_name = self.get_model_name(item["Key"])
            if model_name:
                model_index = census_to_gsafac_model_names.index(model_name)
                model_obj = census_to_gsafac_models[model_index]
                try:
                    file = self.get_s3_object(
                        census_to_gsafac_bucket_name, item["Key"], model_obj
                    )
                    if file:
                        self.load_data(file, model_obj, chunk_size)
                except Exception:
                    logger.info(f"Skipping {model_name}")

        self.display_row_counts(census_to_gsafac_models)

    def display_row_counts(self, models):
        for mdl in models:
            row_count = mdl.objects.all().count()
            logger.info(f"{row_count} in {mdl}")

    def delete_data(self):
        for mdl in census_to_gsafac_models:
            logger.info("Deleting %s", mdl)
            mdl.objects.all().delete()

    def sample_data(self):
        for mdl in census_to_gsafac_models:
            logger.info("Sampling %s", mdl)
            rows = mdl.objects.all()[:1]
            for row in rows:
                for col in mdl._meta.fields:
                    logger.info(f"{col.name}: {getattr(row, col.name)}")

    def list_s3_objects(self, bucket_name, folder):
        return s3_client.list_objects(Bucket=bucket_name, Prefix=folder)["Contents"]

    def get_s3_object(self, bucket_name, key, model_obj):
        file = BytesIO()
        try:
            s3_client.download_fileobj(Bucket=bucket_name, Key=key, Fileobj=file)
        except ClientError:
            logger.error("Could not download {}".format(model_obj))
            return None
        logger.info(f"Obtained {model_obj} from S3")
        return file

    def get_model_name(self, name):
        logger.info("Processing %s", name)
        file_name = name.split("/")[-1].split(".")[0]
        for model_name in census_to_gsafac_model_names:
            if file_name.lower().startswith(model_name):
                logger.info("model_name = %s", model_name)
                return model_name
        logger.error("Could not find a matching model for ", name)
        return None

    def load_data(self, file, model_obj, chunk_size):
        dtypes = defaultdict(lambda: str)
        logger.info("Starting load data to postgres")
        file.seek(0)
        rows_loaded = 0
        for df in pd.read_csv(file, iterator=True, chunksize=chunk_size, dtype=dtypes):
            # Each row is a dictionary. The columns are the
            # correct names for our model. So, this should be a
            # clean way to load the model from a row.
            df = df.replace(np.nan, "")
            for _, row in df.iterrows():
                obj = model_obj(**row)
                obj.save()
            rows_loaded += df.shape[0]
            logger.info(f"Loaded {rows_loaded} rows in {model_obj}")
        return None
