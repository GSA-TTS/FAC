import logging
import boto3
import io


from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

c2g_models = list(apps.get_app_config("c2g").get_models())
c2g_model_names = [m._meta.model_name for m in c2g_models]
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
)
c2g_bucket_name = settings.AWS_C2G_BUCKET_NAME
DELIMITER = ","


class Command(BaseCommand):
    help = """
        Populate PG database from csv files
        Usage:
        manage.py raw_to_pg --folder <folder_name> --clean <True|False>
    """

    def add_arguments(self, parser):
        parser.add_argument("--folder", help="S3 folder name")
        parser.add_argument("--clean")
        parser.add_argument("--sample")

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
            Bucket=c2g_bucket_name,
            Prefix=folder,
        )["Contents"]
        for item in items:
            if item["Key"].endswith("/"):
                continue
            model_name = self.get_model_name(item["Key"])
            if model_name:
                model_obj = c2g_models[c2g_model_names.index(model_name)]
                response = s3_client.get_object(Bucket=c2g_bucket_name, Key=item["Key"])
                rows = io.BytesIO(response["Body"].read())
                self.load_table(model_obj, rows)

        for mdl in c2g_models:
            row_count = mdl.objects.all().count()
            print(f"{row_count} in ", mdl)

    def delete_data(self):
        for mdl in c2g_models:
            print("Deleting ", mdl)
            mdl.objects.all().delete()

    def sample_data(self):
        for mdl in c2g_models:
            print("Sampling ", mdl)
            rows = mdl.objects.all()[:1]
            for row in rows:
                for col in mdl._meta.fields:
                    print(f"{col.name}: {getattr(row, col.name)}")

    def get_model_name(self, name):
        print("Processing ", name)
        file_name = name.split("/")[-1].split(".")[0]
        for model_name in c2g_model_names:
            if file_name.lower().startswith(model_name):
                return model_name
        print("Could not find a matching model for ", name)
        return None

    def load_table(self, model_obj, rows):
        row_list = list(rows)
        column_names = row_list[0].decode("utf-8").split(DELIMITER)
        column_names = [cn.lower().rstrip() for cn in column_names]
        for i in range(1, len(row_list)):
            model_instance = model_obj()
            row = row_list[i].decode("utf-8").split(DELIMITER)
            for column_name in column_names:
                if column_name == "id":
                    continue
                column_number = column_names.index(column_name)
                if column_number >= len(row):
                    print(
                        "Ignoring trailing column ",
                        column_number,
                        column_name,
                        " in row ",
                        i,
                        " in model ",
                        model_obj,
                    )
                else:
                    value = row[column_number].rstrip()
                    setattr(model_instance, column_name, value)
                    model_instance.save()
            if i % 1000 == 0:
                print(f"Loaded {i} of {len(row_list) -1} rows to ", model_obj)
        print(f"Loaded {len(row_list) -1} rows to ", model_obj)
