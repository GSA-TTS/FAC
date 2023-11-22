from census_historical_migration.sac_general_lib.utils import _census_date_to_datetime


# FIXME: Get the padding/shape right on the report_id
def dbkey_to_report_id(Gen, dbkey):
    g = Gen.select(Gen.audityear, Gen.fyenddate).where(Gen.dbkey == dbkey).get()
    # month = g.fyenddate.split('-')[1]
    # 2022JUN0001000003
    # We start new audits at 1 million.
    # So, we want 10 digits, and zero-pad for
    # historic DBKEY report_ids
    dt = _census_date_to_datetime(g.fyenddate)
    return f"{g.audityear}-{dt.month:02}-CENSUS-{dbkey.zfill(10)}"
