from django.core.management.base import BaseCommand

from psycopg2._psycopg import connection

from django.conf import settings


class Command(BaseCommand):
    help = """
    Runs sql scripts in data_distro/api_views to recreate views for the postgrest API.

    Use -f to specify one file to recreate views in that file.

    """

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, help="file name")

    def handle(self, *args, **kwargs):
        if kwargs["file"] is not None:
            files = [kwargs["file"]]
        else:
            files = ["basic_views.sql", "findings.sql", "general.sql"]

        cloudgov = ["DEVELOPMENT", "PREVIEW", "STAGING", "PRODUCTION"]
        if settings.ENVIRONMENT not in cloudgov:
            conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
        else:
            conn_string = settings.CONNECTION_STRING

        for filename in files:
            conn = connection(conn_string)
            conn.autocommit = True
            with conn.cursor() as curs:
                filename = f"data_distro/api_views/{filename}"
                sql = open(filename, "r").read()
                curs.execute(sql)
