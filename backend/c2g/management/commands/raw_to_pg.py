import logging
import boto3
import io


from django.core.management.base import BaseCommand
from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

c2f_models = list(apps.get_app_config("c2g").get_models())
c2f_model_names = [m._meta.model_name for m in c2f_models]
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_PRIVATE_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_PRIVATE_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
)
c2f_bucket_name = settings.AWS_C2F_BUCKET_NAME


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--folder", help="S3 folder name", required=True)

    def handle(self, *args, **options):
        print("c2f_model_names", c2f_model_names)
        items = s3_client.list_objects(
            Bucket=c2f_bucket_name,
            Prefix=options["folder"],
        )["Contents"]
        for item in items:
            if item["Key"].endswith("/"):
                continue
            model_name = self.get_model_name(item["Key"])
            if model_name:
                model_obj = c2f_models[c2f_model_names.index(model_name)]
                response = s3_client.get_object(Bucket=c2f_bucket_name, Key=item["Key"])
                rows = io.BytesIO(response["Body"].read())
                self.load_table(model_obj, rows)

    def get_model_name(self, name):
        print(f"Checking raw file name {name}")
        name = name.split("/")[-1].split(".")[0]
        print(f"Checking file name {name}")
        for model_name in c2f_model_names:
            # m_suffix = m[len("census") :]
            if name.lower().startswith(model_name):
                return model_name
        print("Could not find a matching model")
        return None

    def load_table(self, model_obj, rows):
        row_list = list(rows)
        column_names = row_list[0].decode("utf-8").split("|")
        column_names = [cn.lower().rstrip() for cn in column_names]
        for i in range(1, 10):
            print(f"Loading {i} of {len(row_list) -1} rows ")
            if i > len(row_list) - 1:
                continue
            model_instance = model_obj()
            row = row_list[i].decode("utf-8").split("|")
            for column_name in column_names:
                column_number = column_names.index(column_name)
                if column_number >= len(row):
                    print(
                        "Ignoring trailing column ",
                        column_number,
                        column_name,
                        " in row ",
                        i,
                    )
                else:
                    value = row[column_number].rstrip()
                    setattr(model_instance, column_name, value)
                    model_instance.save()
