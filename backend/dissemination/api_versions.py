from psycopg2._psycopg import connection
from config import settings

# These are API versions we want live.
live = [
    "api_v1_0_0_beta",
]

# These versions will have their schemas dropped
# in a cascade
deprecated = [

]


def get_conn_string():
    # Default to the production connection string
    conn_string = None
    if settings.ENVIRONMENT not in ["DEVELOPMENT", "STAGING", "PRODUCTION"]:
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

def create_api(version):
    for filename in ["create_schema.sql", "create_views.sql"]:
        exec_sql(version, filename)

def drop_api(version):
    for filename in ["drop.sql"]:
        exec_sql(version, filename)

def create_live_apis():
    for version in live:
        create_api(version)
        
def deprecate_apis():
    for version in deprecated:
        drop_api(version)

