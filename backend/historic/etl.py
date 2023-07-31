import pandas as pd

from .mapper import mapper
from .models import ELECAUDITHEADER
from dissemination.models import General
from .mappings import general

# from .db import DB


class ETL:
    def __init__(self, audit_year):
        self.audit_year = audit_year

    def load_general(self):
        c2g_mapper = mapper(general.cfac_to_gfac)
        src_df = pd.DataFrame.from_records(
            ELECAUDITHEADER.objects.all().filter(AUDITYEAR=self.audit_year).values()
        )
        if len(src_df) == 0:
            print("No matching rows in ELECAUDITHEADER")
            return 0

        tgt_df = src_df.copy(deep=True)
        # print("Found Columns to DB:", tgt_df.columns)

        tgt_df = c2g_mapper.apply_mappings_to_df(tgt_df)
        # print("Mapped Columns to DB:", tgt_df.columns)

        tgt_df = c2g_mapper.add_fun_column_to_df(
            tgt_df, "report_id", self.add_report_id
        )
        tgt_df = c2g_mapper.add_const_column_to_df(tgt_df, "data_source", "Census")

        gen_rows = [General(**row) for row in tgt_df.to_dict("records")]
        # TODO Implement error handling. Errors should be looged to a file,
        General.objects.bulk_create(gen_rows, ignore_conflicts=True)

        # DB().write_df_to_sql(tgt_df, "dissemination_general")

    # TODO Implement a formula compatible with G_FAC report_id
    def add_report_id(self, row):
        r_id = (
            str(row["audit_year"]) + str(row["fy_start_date"])[4:8] + str(row.name)[:10]
        )
        return r_id
