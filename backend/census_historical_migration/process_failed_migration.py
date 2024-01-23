import logging

from .historic_data_loader import (
    create_or_get_user,
    log_results,
    perform_migration,
)
from .models import ELECAUDITHEADER as AuditHeader, ReportMigrationStatus

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

User = get_user_model()


def reprocess_failed_reports(audit_year, page_size, pages, error_tag):
    """Iterates over and processes submissions for the given audit year"""
    total_count = error_count = 0
    user = create_or_get_user()
    failed_migrations = (
        ReportMigrationStatus.objects.filter(
            audit_year=audit_year,
            migration_status="FAILURE",
            migrationerrordetail__tag=error_tag,
        )
        .order_by("id")
        .distinct()
    )

    paginator = Paginator(failed_migrations, page_size)

    logger.info(
        f"{failed_migrations.count()} reports have failed migration with error tag {error_tag}"
    )

    for page_number in pages:
        if page_number <= paginator.num_pages:
            page = paginator.page(page_number)
            if page.object_list.count() > 0:
                dbkey_list = [status.dbkey for status in page.object_list]

                submissions = AuditHeader.objects.filter(
                    DBKEY__in=dbkey_list, AUDITYEAR=audit_year
                )
                logger.info(
                    f"Processing page {page_number} with {submissions.count() if submissions else 0} submissions."
                )
                total_count, error_count = perform_migration(
                    user, submissions, total_count, error_count
                )
        else:
            logger.info(f"Skipping page {page_number} as it is out of range")

    log_results(error_count, total_count)
