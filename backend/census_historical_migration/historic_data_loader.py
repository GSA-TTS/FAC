import logging
from .models import ELECAUDITHEADER as AuditHeader
from .end_to_end_core import run_end_to_end

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

User = get_user_model()


def load_historic_data_for_year(audit_year, page_size, pages):
    """Iterates over and processes submissions for the given audit year"""
    result_log = {}
    total_count = error_count = 0
    user = create_or_get_user()
    submissions_for_year = AuditHeader.objects.filter(AUDITYEAR=audit_year).order_by(
        "ELECAUDITHEADERID"
    )
    paginator = Paginator(submissions_for_year, page_size)

    logger.info(f"{submissions_for_year.count()} submissions found for {audit_year}")

    for page_number in pages:
        page = paginator.page(page_number)
        logger.info(
            f"Processing page {page_number} with {page.object_list.count()} submissions."
        )

        for submission in page.object_list:
            result = {"success": [], "errors": []}
            # Migrate a single submission
            run_end_to_end(user, submission, result)

            result_log[(submission.AUDITYEAR, submission.DBKEY)] = result
            total_count += 1

            has_failed = len(result["errors"]) > 0
            if has_failed:
                error_count += 1
            if total_count % 5 == 0:
                logger.info(f"Processed = {total_count}, Errors = {error_count}")

    log_results(result_log, error_count, total_count)


def log_results(result_log, error_count, total_count):
    """Prints the results of the migration"""

    logger.info("********* Loader Summary ***************")

    for k, v in result_log.items():
        logger.info(f"{k}, {v}")
        logger.info("-------------------")

    logger.info(f"{error_count} errors out of {total_count}")


def create_or_get_user():
    """Returns the default migration user"""
    user_email = "fac-census-migration-auditee-official@fac.gsa.gov"
    user_name = "fac-census-migration-auditee-official"
    user = None

    users = User.objects.filter(email=user_email)
    if users:
        user = users.first()
    else:
        logger.info("Creating user %s %s", user_email, user_name)
        user = User(username=user_name, email=user_email)
        user.save()

    return user
