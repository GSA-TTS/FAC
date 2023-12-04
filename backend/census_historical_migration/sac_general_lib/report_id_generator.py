from ..sac_general_lib.utils import (
    xform_census_date_to_datetime,
)


def xform_dbkey_to_report_id(audit_header, dbkey):
    # month = audit_header.fyenddate.split('-')[1]
    # 2022JUN0001000003
    # We start new audits at 1 million.
    # So, we want 10 digits, and zero-pad for
    # historic DBKEY report_ids
    dt = xform_census_date_to_datetime(audit_header.FYENDDATE)
    return f"{audit_header.AUDITYEAR}-{dt.month:02}-CENSUS-{dbkey.zfill(10)}"
