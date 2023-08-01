import pandas as pd


from .mapper import mapper
from .models import ELECAUDITHEADER, ELECAUDITS
from dissemination.models import General, FederalAward
from .mappings import general, federalaward

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
        print(f"Processing {len(src_df)} rows in ELECAUDITHEADER")

        tgt_df = src_df.copy(deep=True)

        tgt_df = c2g_mapper.apply_mappings_to_df(tgt_df, make_report_id=True)
        tgt_df = c2g_mapper.add_const_column_to_df(tgt_df, "data_source", "Census")

        gen_rows = [General(**row) for row in tgt_df.to_dict("records")]
        # TODO Implement error handling. Errors should be looged to a file,
        General.objects.bulk_create(gen_rows, ignore_conflicts=False)

    def load_award(self):
        c2g_mapper = mapper(federalaward.cfac_to_gfac)
        src_df = pd.DataFrame.from_records(
            ELECAUDITS.objects.all().filter(AUDITYEAR=self.audit_year).values()
        )
        if len(src_df) == 0:
            print("No matching rows in ELECAUDITS")
            return 0
        print(f"Processing {len(src_df)} rows in ELECAUDITS")

        tgt_df = src_df.copy(deep=True)

        tgt_df = c2g_mapper.apply_mappings_to_df(tgt_df)

        award_rows = [FederalAward(**row) for row in tgt_df.to_dict("records")]

        # TODO Implement error handling. Errors should be looged to a file,
        FederalAward.objects.bulk_create(award_rows, ignore_conflicts=False)
