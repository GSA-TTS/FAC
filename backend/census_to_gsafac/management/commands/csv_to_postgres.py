import logging
import boto3
import csv


from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

census_to_gsafac_models = list(apps.get_app_config("census_to_gsafac").get_models())
census_to_gsafac_model_names = [m._meta.model_name for m in census_to_gsafac_models]
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
)
census_to_gsafac_bucket_name = settings.AWS_CENSUS_TO_GSAFAC_BUCKET_NAME
DELIMITER = ","


class Command(BaseCommand):
    help = """
        Populate Postgres database from csv files
        Usage:
        manage.py csv_to_postgres --folder <folder_name> --clean <True|False>
    """

    def add_arguments(self, parser):
        parser.add_argument("--folder", help="S3 folder name")
        parser.add_argument("--clean")
        parser.add_argument("--sample")
        parser.add_argument("--load")

    def handle(self, *args, **options):
        if options.get("clean") == "True":
            self.delete_data()
            return
        if options.get("sample") == "True":
            self.sample_data()
            return

        folder = options.get("folder")
        if not folder:
            print("Please specify a folder name")
            return

        items = s3_client.list_objects(
            Bucket=census_to_gsafac_bucket_name,
            Prefix=folder,
        )["Contents"]
        for item in items:
            if item["Key"].endswith("/"):
                continue
            model_name = self.get_model_name(item["Key"])
            if model_name:
                model_obj = census_to_gsafac_models[
                    census_to_gsafac_model_names.index(model_name)
                ]
                response = s3_client.get_object(
                    Bucket=census_to_gsafac_bucket_name, Key=item["Key"]
                )
                print("Obtained response from S3")
                lines = response["Body"].read().decode("utf-8").splitlines(True)
                print("Loaded Body into 'lines'")
                rows = [row for row in csv.DictReader(lines)]
                print("Completed processing 'lines'")
                self.load_table(model_obj, rows)

        for mdl in census_to_gsafac_models:
            row_count = mdl.objects.all().count()
            print(f"{row_count} in ", mdl)

    def delete_data(self):
        for mdl in census_to_gsafac_models:
            print("Deleting ", mdl)
            mdl.objects.all().delete()

    def sample_data(self):
        for mdl in census_to_gsafac_models:
            print("Sampling ", mdl)
            rows = mdl.objects.all()[:1]
            for row in rows:
                for col in mdl._meta.fields:
                    print(f"{col.name}: {getattr(row, col.name)}")

    def get_model_name(self, name):
        print("Processing ", name)
        file_name = name.split("/")[-1].split(".")[0]
        for model_name in census_to_gsafac_model_names:
            if file_name.lower().startswith(model_name):
                print("model_name = ", model_name)
                return model_name
        print("Could not find a matching model for ", name)
        return None

    def load_table(self, model_obj, rows):
        print("Loading data for model_obj ", model_obj)
        for i in range(0, len(rows)):
            model_instance = model_obj()

            for column_name, value in rows[i].items():
                if column_name == "id":
                    continue
                setattr(model_instance, column_name, value)
            model_instance.save()
            if i % 1000 == 0:
                print(f"Loaded {i} of {len(rows)} rows to ", model_obj)
        print(f"Loaded {len(rows)} rows to ", model_obj)
