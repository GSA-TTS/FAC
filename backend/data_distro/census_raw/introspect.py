from peewee import SqliteDatabase
from playhouse.reflection import generate_models, print_model, print_table_sql
from peewee import *

# Connect to a Postgres database.
pg_db = PostgresqlDatabase('postgres', user='postgres',
                           host='localhost', port=5432)

models = generate_models(pg_db)
globals().update(models)