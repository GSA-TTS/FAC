from psycopg2._psycopg import connection
from config import settings
import logging
import os

logger = logging.getLogger(__name__)

# These are API versions we want live.
live = {"dissemination": ["api_v1_0_3", "api_v1_1_0"], "support": ["admin_api_v1_1_0"]}

# These are API versions we have deprecated.
# They will be removed. It should be safe to leave them
# here for repeated runs.
deprecated = {"dissemination": ["api"], "support": []}


def get_conn_string():
    # Default to the production connection string
    conn_string = None
    if settings.ENVIRONMENT in ["LOCAL", "TESTING"]:
        conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
    else:
        conn_string = settings.CONNECTION_STRING
    return conn_string


def exec_sql_at_path(dir, filename):
    conn = connection(get_conn_string())
    conn.autocommit = True
    path = os.path.join(dir, filename)
    with conn.cursor() as curs:
        logger.info(f"EXEC SQL {path}")
        sql = open(path, "r").read()
        curs.execute(sql)


def exec_sql(location, version, filename):
    conn = connection(get_conn_string())
    conn.autocommit = True
    with conn.cursor() as curs:
        path = f"{location}/api/{version}/{filename}"
        logger.info(f"EXEC SQL {location} {version} {filename}")
        sql = open(path, "r").read()
        curs.execute(sql)


def create_views(location, version):
    exec_sql(location, version, "create_views.sql")


def drop_views(location, version):
    exec_sql(location, version, "drop_views.sql")


def create_schema(location, version):
    exec_sql(location, version, "create_schema.sql")


def drop_schema(location, version):
    exec_sql(location, version, "drop_schema.sql")


def create_live_schemas(location):
    for version in live[location]:
        drop_schema(location, version)
        exec_sql(location, version, "base.sql")
        create_schema(location, version)


def drop_live_schema(location):
    for version in live[location]:
        drop_schema(location, version)


def drop_live_views(location):
    for version in live[location]:
        drop_views(location, version)


def create_live_views(location):
    for version in live[location]:
        drop_views(location, version)
        create_views(location, version)


def create_functions(location):
    for version in live[location]:
        exec_sql(location, version, "create_functions.sql")


def deprecate_schemas_and_views(location):
    for version in deprecated[location]:
        exec_sql(location, version, "drop_schema.sql")


def create_access_tables(location):
    for version in live[location]:
        exec_sql(location, version, "create_access_tables.sql")
