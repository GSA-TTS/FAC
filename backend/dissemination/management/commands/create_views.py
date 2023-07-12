from django.core.management.base import BaseCommand

from psycopg2._psycopg import connection

from django.conf import settings

import sys


class Command(BaseCommand):
    help = """
    Runs sql scripts  to recreate views for the postgrest API.

    Use -f to specify one file to recreate views in that file.

    """

    def add_arguments(self, parser):
        parser.add_argument("-f", "--file", type=str, help="file name")
        parser.add_argument("-a", "--api_version", type=str, help="API version")

    def handle(self, *args, **kwargs):
        files = None
        api_version = None

        if kwargs["api_version"] is None:
            print("API version must be provided to create views. Exiting.")
            sys.exit(-1)
        else:
            api_version = kwargs["api_version"]

        if kwargs["file"] is None:
            files = [
                f"init_api_db.sql",
                f"db_views.sql",
            ]

        if settings.ENVIRONMENT not in ["DEVELOPMENT", "STAGING", "PRODUCTION"]:
            conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
        else:
            conn_string = settings.CONNECTION_STRING

        for filename in files:
            conn = connection(conn_string)
            conn.autocommit = True
            with conn.cursor() as curs:
                filename = f"dissemination/api/{api_version}/{filename}"
                sql = open(filename, "r").read()
                curs.execute(sql)
