from django.core.management.base import BaseCommand
from django.db.models import Q

import logging

from audit.models import Audit
from dissemination.models import General
from audit.models.utils import validate_audit_consistency

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
        For the given fac_accepted_date range, validate that submission data
        matches for both the SOT and SAC models.
        Usage:
        manage.py source_of_truth
            --start <YYYY-MM-DD start fac_accepted_date>
            --end <YYYY-MM-DD end fac_accepted_date>
            -- limit <int>

        Alternatively, it can also test on a single report_id:
        manage.py source_of_truth
            --report_id 2023-12-GSAFAC-0000000001
    """

    def add_arguments(self, parser):
        parser.add_argument("--start", type=str, required=False, help="YYYYMMDD start fac_accepted_date")
        parser.add_argument("--end", type=str, required=False, help="YYYYMMDD end fac_accepted_date")
        parser.add_argument("--report_id", type=str, required=False, help="A report_id")
        parser.add_argument("--limit", type=int, required=False, help="Limit the number of audits to test")

    def handle(self, *args, **kwargs):
        report_id = kwargs.get("report_id", None)
        if report_id:
            logger.info(f"Testing on report_id {report_id}")
            query = Q(report_id=report_id)
            limit = 1
        else:
            start = kwargs["start"]
            end = kwargs["end"]
            logger.info(f"Testing on date range {start}-{end}")
            query = Q(fac_accepted_date__gte=start) & Q(fac_accepted_date__lte=end)
            limit = kwargs.get("limit", None)

        sot_audits_query = Audit.objects.filter(query & Q(submission_status='disseminated')).order_by('report_id')[:limit]
        sot_sorted_report_ids = self._get_sorted_report_ids(sot_audits_query)

        gen_audits_query = General.objects.filter(query).order_by('report_id')[:limit]
        sac_sorted_report_ids = self._get_sorted_report_ids(gen_audits_query)

        logger.info(f"SOT report_ids: {sot_sorted_report_ids}")
        logger.info(f"SAC report_ids: {sac_sorted_report_ids}")

        if sot_sorted_report_ids != sac_sorted_report_ids:
            sot_not_sac = [x for x in sot_sorted_report_ids if x not in sac_sorted_report_ids]
            logger.error(f"report_ids found in SOT but not SAC: {sot_not_sac}")
            sac_not_sot = [x for x in sac_sorted_report_ids if x not in sot_sorted_report_ids]
            logger.error(f"report_ids found in SAC but not SOT: {sac_not_sot}")
        else:
            logger.info(f"SOT and SAC report_ids match; continuing")

        sot_audits_by_report_id = self._get_audits_by_report_id(sot_audits_query)

        for report_id in sot_sorted_report_ids:
            is_consistent, differences = validate_audit_consistency(sot_audits_by_report_id[report_id])

            if not is_consistent:
                logger.error(f"Differences found for {report_id}:")
                logger.error(differences)

    def _get_sorted_report_ids(self, queryset):
        # The query results are already ORDER_BYed report_id, so no need to
        # sort again
        report_ids = []
        for audit in queryset:
            report_ids.append(audit.report_id)

        return report_ids

    def _get_audits_by_report_id(self, audits_query):
        result = {}
        for audit in audits_query:
            result[audit.report_id] = audit

        return result
