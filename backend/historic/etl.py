import pandas as pd


from .mapper import mapper
from .models import ELECAUDITHEADER, ELECAUDITS
from dissemination.models import General, FederalAward
from .mappings import general, federalaward

# from .db import DB


class ETL:
    MAKE_REPORT_ID = True

    def __init__(self, audit_year):
        self.audit_year = audit_year
        self.specs = [
            (
                "ELECAUDITHEADER",
                ELECAUDITHEADER,
                General,
                general.cfac_to_gfac,
                self.MAKE_REPORT_ID,
            ),
            (
                "ELECAUDITS",
                ELECAUDITS,
                FederalAward,
                federalaward.cfac_to_gfac,
                not self.MAKE_REPORT_ID,
            ),
        ]

    def load_history(self):
        for spec in self.specs:
            self._load_table(spec)

    def _load_table(self, spec):
        table, src_obj, tgt_obj, s2t_map, make_report_id = spec
        c2g_mapper = mapper(s2t_map)
        df = pd.DataFrame.from_records(
            src_obj.objects.all().filter(AUDITYEAR=self.audit_year).values()
        )
        if len(df) == 0:
            print(f"No matching rows in {table}")
            return 0
        print(f"Processing {len(df)} rows in {table}")

        df = c2g_mapper.apply_mappings_to_df(df, make_report_id)

        rows = [tgt_obj(**row) for row in df.to_dict("records")]
        # TODO Implement error handling. Errors should be looged to a file,
        tgt_obj.objects.bulk_create(rows, ignore_conflicts=False)
