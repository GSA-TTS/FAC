from django.core.management.base import BaseCommand

from psycopg2._psycopg import connection

from django.conf import settings


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate views for the postgrest API.

    Use -f to specify one file to recreate views in that file.

    """

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, help="file name")

    def handle(self, *args, **kwargs):
        if kwargs["file"] is not None:
            files = [kwargs["file"]]
        else:
            files = [
                "init_api_db.sql",
                "db_views.sql",
            ]

        if settings.ENVIRONMENT not in ["DEVELOPMENT", "STAGING", "PRODUCTION"]:
            conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
        else:
            conn_string = settings.CONNECTION_STRING

        for filename in files:
            conn = connection(conn_string)
            conn.autocommit = True
            with conn.cursor() as curs:
                filename = f"dissemination/api/{filename}"
                sql = open(filename, "r").read()
                curs.execute(sql)
