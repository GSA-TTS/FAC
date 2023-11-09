from datetime import datetime
from django.core.management.base import BaseCommand
from config import settings
from django.db import connection, models
from django.apps import apps


class Command(BaseCommand):
    help = """
    Collect metrics about the database and media.
    For the database, list table, row count and size
    For media files, list file types, create date and size
    """

    def handle(self, *args, **kwargs):
        print(f"Metrics for {settings.ENVIRONMENT} collected at {datetime.now()}")
        self.dump_db_metrics()
        self.dump_media_metrics()

    def dump_db_metrics(self):
        def get_table_size(model):
            cursor = connection.cursor()
            cursor.execute(f"SELECT pg_total_relation_size('{model._meta.db_table}');")
            table_size = cursor.fetchone()[0]
            cursor.close()
            return table_size

        total_size = 0
        for app in apps.get_app_configs():
            print(f"App: {app.name}:")
            for model in app.get_models():
                row_count = model.objects.count()
                table_size = get_table_size(model)
                total_size += table_size
                print(
                    f"  * {model._meta.verbose_name}: {row_count} rows, {table_size} bytes"
                )
        print(f" ** Database size: {total_size} bytes **")

    def dump_media_metrics(self):
        total_size = 0
        for app in apps.get_app_configs():
            for model in app.get_models():
                for field in model._meta.get_fields():
                    if isinstance(field, models.FileField):
                        print(
                            f"{app.name} : {model._meta.verbose_name} : {field.name}:"
                        )
                        count = size = 0
                        for row in model.objects.all():
                            count += 1
                            size += getattr(row, field.name).file.size
                        print(f"{count} instances, {size} bytes")
                        total_size += size
        print(f" ** Media size: {total_size} bytes **")
