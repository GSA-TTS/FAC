from datetime import date


def _census_date_to_datetime(cd):
    lookup = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
    }
    parts = cd.split("-")
    if len(parts) != 3 or parts[1] not in lookup:
        raise ValueError("Invalid date format or month abbreviation in census date")
    year, month_abbr, day = parts
    month = lookup[month_abbr]
    return date(year + 2000, month, day)


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
