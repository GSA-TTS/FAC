from psycopg2._psycopg import connection
from config import settings

# These are API versions we want live.
live = {
    "dissemination": ["api_v1_0_3"],
    "support": ["admin_api_v1_0_0"]
}

# These are API versions we have deprecated.
# They will be removed. It should be safe to leave them
# here for repeated runs.
deprecated = {
    "dissemination": ["api", "api_v1_0_0", "api_v1_0_1", "api_v1_0_2"],
    "support": []
    }


def get_conn_string():
    # Default to the production connection string
    conn_string = None
    if settings.ENVIRONMENT not in ["DEVELOPMENT", "PREVIEW", "STAGING", "PRODUCTION"]:
        conn_string = "dbname='postgres' user='postgres' port='5432' host='db'"
    else:
        conn_string = settings.CONNECTION_STRING
    return conn_string


def exec_sql(location, version, filename):
    conn = connection(get_conn_string())
    conn.autocommit = True
    with conn.cursor() as curs:
        filename = f"{location}/api/{version}/{filename}"
        sql = open(filename, "r").read()
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
        exec_sql(location, version, "drop.sql")
