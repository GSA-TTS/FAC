"""
The intent of this file is to group together audit related helpers.
"""

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Func


def generate_sac_report_id(count, end_date, source="GSAFAC"):
    """
    Convenience method for generating report_id, a value consisting of:

        -   Four-digit year based on submission fiscal end date.
        -   Two-digit month based on submission fiscal end date.
        -   Audit source: either GSAFAC or CENSUS.
        -   Zero-padded 10-digit numeric monotonically increasing.
        -   Separated by hyphens.

    For example: `2023-09-GSAFAC-0000000001`, `2020-09-CENSUS-0000000001`.
    """
    source = source.upper()
    if source not in ("CENSUS", "GSAFAC"):
        raise Exception("Unknown source for report_id")
    year, month, _ = end_date.split("-")
    if not (2000 <= int(year) < 2200):
        raise Exception("Unexpected year value for report_id")
    if int(month) not in range(1, 13):
        raise Exception("Unexpected month value for report_id")
    separator = "-"
    report_id = separator.join([year, month, source, str(count).zfill(10)])
    return report_id


class JsonArrayToTextArray(Func):
    function = "json_array_to_text_array"
    output_field = ArrayField(models.CharField())
