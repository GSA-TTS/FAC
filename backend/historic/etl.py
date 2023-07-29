import pandas as pd

from .mapper import mapper
from .models import ELECAUDITHEADER
from .mappings import general
from .db import DB


class ETL:
    def __init__(self, audit_year):
        self.audit_year = audit_year

    def load_general(self):
        c2g_mapper = mapper(general.cfac_to_gfac)
        src_df = pd.DataFrame.from_records(
            ELECAUDITHEADER.objects.all().filter(AUDITYEAR=self.audit_year).values()
        )
        tgt_df = src_df.copy(deep=True)
        tgt_df = c2g_mapper.apply_mappings_to_df(tgt_df)
        tgt_df = c2g_mapper.add_fun_column_to_df(
            tgt_df, "report_id", self.add_report_id
        )
        tgt_df = c2g_mapper.add_const_column_to_df(tgt_df, "data_source", "Census")
        print("Writing to DB:", tgt_df)
        DB().write_df_to_sql(tgt_df, "dissemination_general")

    def add_report_id(self, row):
        return str(row["audit_year"]) + str(row["fy_start_date"])
