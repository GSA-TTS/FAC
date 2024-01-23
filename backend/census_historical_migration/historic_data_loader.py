import logging
from .models import ELECAUDITHEADER as AuditHeader
from .migration_result import MigrationResult
from .end_to_end_core import run_end_to_end

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

User = get_user_model()


def load_historic_data_for_year(audit_year, page_size, pages):
    """Iterates over and processes submissions for the given audit year"""
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
        total_count, error_count = perform_migration(
            user, page.object_list, total_count, error_count
        )
    log_results(error_count, total_count)


def perform_migration(user, submissions, round_count, total_error_count):
    total_count = round_count
    error_count = total_error_count
    for submission in submissions:
        # Migrate a single submission
        run_end_to_end(user, submission)
        total_count += 1
        if MigrationResult.has_errors():
            error_count += 1
        if total_count % 5 == 0:
            logger.info(f"Processed = {total_count}, Errors = {error_count}")
        MigrationResult.append_summary(submission.AUDITYEAR, submission.DBKEY)

    return total_count, error_count


def log_results(error_count, total_count):
    """Prints the results of the migration"""

    logger.info("********* Loader Summary ***************")

    for k, v in MigrationResult.result["summaries"].items():
        logger.info(f"{k}, {v}")
        logger.info("-------------------")

    logger.info(f"{error_count} errors out of {total_count}")
    MigrationResult.reset()


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
