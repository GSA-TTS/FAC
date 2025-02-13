import logging

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from django.db import connection

from audit.models import Audit
from audit.views.views import _index_findings

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        queryset = Audit.objects.raw(
            "select * from audit_audit "
            "where corrected is false "
            "order by id desc limit 50000")
        paginator = Paginator(queryset, 100)  # 100 items per page

        for page_num in paginator.page_range:
            logger.info("Processing page %s", page_num)
            page = paginator.page(page_num)
            for audit in page.object_list:
                try:
                    findings_summary = _index_findings(audit.audit).get("findings_summary")
                    audit.audit.update({"search_indexes": {"findings_summary": findings_summary}})
                    audit.save()
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"update audit_audit set corrected = true where report_id = '{audit.report_id}'")
                except Exception as e:
                    logger.error(f"Failed to migrate sac {audit.report_id} - {e}")
                    raise e
