# Pandas only supports SQLAlchemy engine/connection ob
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

from .mapper import mapper
from config import settings


class DB:
    def __init__(self, db="postgres", driver="postgresql+psycopg2"):
        self.db_settings = settings.DATABASES["default"]
        # db = db_settings['NAME']
        user = self.db_settings["USER"]
        password = self.db_settings["PASSWORD"]
        port = self.db_settings["PORT"] or 5432
        host = self.db_settings["HOST"]

        # Pandas only wants SQLAlchemy engine objects.
        # I don't know if we can get those from Django. If so, this code
        # should change. If not... then someday, we'll want DB objects
        # to be able to talk to different DBs, as the historical data
        # will live outside of the production/app DB.
        self.connection_string = f"{driver}://{user}:{password}@{host}:{port}"
        self.connect()
        self.df_set = False

    def connect(self):
        print("Creating engine:", self.connection_string)
        self.engine = create_engine(self.connection_string)
        print("Engine created. Connecting ...")
        self.connection = self.engine.connect()

    def close(self):
        self.connection.close()

    def read_sql_to_df(self, query):
        self.df_set = True
        self.df = pd.read_sql_query(query, self.connection)

    def get_df(self) -> pd.DataFrame:
        return self.df

    # Fun consumes (df, ndx)
    # def add_column(self, column, fun):
    #     self.df[column] = np.NaN
    #     for ndx in range(len(self.df)):
    #         self.df.at[ndx, column] = fun(self.df, ndx)

    # I lost an hour to this: pass the engine, not the connection
    # object. Why? I don't know.
    # https://stackoverflow.com/questions/48307008/pandas-to-sql-doesnt-insert-any-data-in-my-table#:~:text=passing%20sqlalchemy%20connection%20object%20instead%20of%20engine%20object%20to%20the%20con%20parameter

    def write_df_to_sql(self, df, dest_table, mode="append"):
        return df.to_sql(
            dest_table,
            self.engine,
            if_exists=mode,
            index=False,
            chunksize=1000,
            # schema="public",
        )

    def append(self, new_df: pd.DataFrame):
        if not self.df_set:
            self.df = new_df.copy()
            self.df_set = True
        else:
            self.df = pd.concat([self.df, new_df.copy()])
