"""
update_oldformat_report_ids command

One-off idempotent command to take SAC instances that have the original report_id format
(<startyear><startmonth3charabbr>GSA<count + 1000000>) and update their report_id
to the new format (<endyear><endmonth2digit>GSAFAC<count>).
"""
import calendar
import logging
import time
from pathlib import Path

from django.core.management.base import BaseCommand

from audit.models import SingleAuditChecklist

logger = logging.getLogger(__name__)


def get_newformat_report_id(sac):
    """
    Given a SAC instance, return the new-format report_id.
    """
    old_report_id = sac.report_id
    end_date = sac.general_information["auditee_fiscal_period_end"]
    end_year, end_month, _day = end_date.split("-")
    count = old_report_id[-10:]
    new_count = int(count) - 1000000 if int(count) > 1000000 else int(count)
    return "-".join((end_year, end_month, "GSAFAC", str(new_count).zfill(10)))


def get_oldformat_report_id(sac):
    """
    Given a SAC instance, return the old-format report_id.

    Works, but needs to be run using a record of what SAC instances were changed in
    order to truly reverse the operation. Such a list could be constructed out of
    the file saved in handle() below.
    """
    fiscal_start = sac.general_information["auditee_fiscal_period_start"]
    year = fiscal_start[:4]
    month = calendar.month_abbr[int(fiscal_start[5:7])].upper()
    count = sac.report_id[-10:]
    oldcount = int(count) + 1000000
    return f"{year}{month}{str(oldcount).zfill(10)}"


class Command(BaseCommand):
    """Django management command to change report_id format."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--reverse",
            action="store_true",
            help="Switch to old-format report_ids instead.",
        )

    def handle(self, *args, **options):
        changesfile = Path(__file__).parent / f"{time.time()}-changed_reportids.txt"
        lines = []
        change_sacs = SingleAuditChecklist.objects.exclude(report_id__contains="GSAFAC")

        for sac in change_sacs:
            old_rid = str(sac.report_id)
            new_rid = get_newformat_report_id(sac)
            sac.report_id = new_rid
            sac.data_source = "GSAFAC"
            sac.save(undocumentedoverride="HACKZ")
            outstring = f"id: {sac.id} old: {old_rid} new: {new_rid}"
            lines.append(outstring)

        contents = "\n".join(lines)
        changesfile.write_text(contents, encoding="utf-8")
