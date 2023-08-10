from psycopg2._psycopg import connection
from config import settings
from typing import List

# These are API versions we want live.
live = [
    # These are API versions we have in flight.
    "api_v1_0_0_beta",
]

# These are API versions we have deprecated.
# They will be removed. It should be safe to leave them
# here for repeated runs.
deprecated: List[str] = ["api"]


def get_conn_string():
    # Default to the production connection string
    conn_string = None
    if settings.ENVIRONMENT not in ["DEVELOPMENT", "PREVIEW", "STAGING", "PRODUCTION"]:
        conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
    else:
        conn_string = settings.CONNECTION_STRING
    return conn_string


def exec_sql(version, filename):
    conn = connection(get_conn_string())
    conn.autocommit = True
    with conn.cursor() as curs:
        filename = f"dissemination/api/{version}/{filename}"
        sql = open(filename, "r").read()
        curs.execute(sql)


def create_views(version):
    exec_sql(version, "create_views.sql")


def drop_views(version):
    exec_sql(version, "drop_views.sql")


def create_schema(version):
    exec_sql(version, "create_schema.sql")


def drop_schema(version):
    exec_sql(version, "drop_schema.sql")


def create_live_schemas():
    for version in live:
        drop_schema(version)
        exec_sql(version, "base.sql")
        create_schema(version)


def drop_live_schema():
    for version in live:
        drop_schema(version)


def drop_live_views():
    for version in live:
        drop_views(version)


def create_live_views():
    for version in live:
        drop_views(version)
        create_views(version)


def create_functions():
    for version in live:
        exec_sql(version, "create_functions.sql")


def deprecate_schemas_and_views():
    for version in deprecated:
        exec_sql(version, "drop.sql")
