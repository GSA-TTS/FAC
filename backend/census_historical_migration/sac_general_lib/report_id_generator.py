from ..transforms.xform_string_to_string import string_to_string
from ..sac_general_lib.utils import (
    xform_census_date_to_datetime,
)


def xform_dbkey_to_report_id(audit_header):
    """Constructs the report ID from the DBKEY.
    The report ID is constructed as follows:
    YYYY-MM-CENSUS-DBKEY."""
    # month = audit_header.fyenddate.split('-')[1]
    # 2022JUN0001000003
    # We start new audits at 1 million.
    # So, we want 10 digits, and zero-pad for
    # historic DBKEY report_ids
    dbkey = string_to_string(audit_header.DBKEY)
    year = string_to_string(audit_header.AUDITYEAR)
    fy_end_date = string_to_string(audit_header.FYENDDATE)
    dt = xform_census_date_to_datetime(fy_end_date)
    return f"{year}-{dt.month:02}-CENSUS-{dbkey.zfill(10)}"
