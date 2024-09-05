from psycopg2._psycopg import connection
from psycopg2.errors import DependentObjectsStillExist
from config import settings
import logging
import os

logger = logging.getLogger(__name__)

# These are API versions we want live.
live = {
    "dissemination": ["api_v1_0_3", "api_v1_1_0"],
    "support": ["admin_api_v1_1_0"],
}

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
        try:
            curs.execute(sql)
        except DependentObjectsStillExist as DOS_err:
            logger.info(f"SQL DEPENDENCY ERR {str(DOS_err)}")
            raise DOS_err
        except Exception as err:
            logger.info(f"SQL UNKNOWN ERR {str(err)}")
            raise err


def exec_sql(location, version, filename):
    conn = connection(get_conn_string())
    conn.autocommit = True
    with conn.cursor() as curs:
        path = f"{location}/api/{version}/{filename}"
        logger.info(f"EXEC SQL {location} {version} {filename}")
        sql = open(path, "r").read()
        try:
            curs.execute(sql)
        except DependentObjectsStillExist as DOS_err:
            logger.info(f"SQL DEPENDENCY ERR {str(DOS_err)}")
            raise DOS_err
        except Exception as err:
            logger.info(f"SQL UNKNOWN ERR {str(err)}")
            raise err


def create_functions(location):
    for version in live[location]:
        exec_sql(location, version, "create_functions.sql")


def create_views(location, version):
    exec_sql(location, version, "create_views.sql")


def drop_views(location, version):
    exec_sql(location, version, "drop_views.sql")


def create_schema(location, version):
    exec_sql(location, version, "create_schema.sql")


def drop_schema(location, version):
    exec_sql(location, version, "drop_schema.sql")


def create_live_views(location):
    """
    Call 'create_views' for each live API version
    """
    for version in live[location]:
        create_views(location, version)


def drop_live_views(location):
    """
    Call 'drop_views' for each live API version
    """
    for version in live[location]:
        drop_views(location, version)


def create_live_schemas(location):
    """
    Execute 'base.sql' then call 'create_schema' for each live API version
    """
    for version in live[location]:
        exec_sql(location, version, "base.sql")
        create_schema(location, version)


def drop_live_schema(location):
    """
    Call 'drop_schema' for each live API version
    """
    for version in live[location]:
        drop_schema(location, version)


def deprecate_schemas_and_views(location):
    """
    Execute 'drop_schema.sql' for all deprecated API versions
    """
    for version in deprecated[location]:
        exec_sql(location, version, "drop_schema.sql")


def create_access_tables(location):
    """
    Execute 'create_access_tables.sql' for each live API version
    """
    for version in live[location]:
        exec_sql(location, version, "create_access_tables.sql")
