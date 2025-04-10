import os
import logging

from config import settings
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sling import Replication, ReplicationStream

logger = logging.getLogger(__name__)

S3_CONNECTION = f"""{{
            "type": "s3",
            "bucket": "{settings.AWS_PRIVATE_STORAGE_BUCKET_NAME}",
            "access_key_id": "{settings.AWS_PRIVATE_ACCESS_KEY_ID}",
            "secret_access_key": "{settings.AWS_PRIVATE_SECRET_ACCESS_KEY}",
            "endpoint": "{settings.AWS_S3_ENDPOINT_URL}",
            "region":"{settings.AWS_S3_PRIVATE_REGION_NAME}"
         }}
    """
DB_URL = os.environ.get("DATABASE_URL")
FAC_DB_URL = (
    f"{DB_URL}?sslmode=disable" if settings.ENVIRONMENT in ["LOCAL", "TEST"] else DB_URL
)
DEFAULT_OPTIONS = {
    "target_options": {
        "format": "csv",
        "compression": "none",
        "file_max_rows": 0,
    }
}


class StreamGenerator:
    def __init__(self, query=None):
        self.query = query

    def generate_stream_inspection(self, audit_year):
        table_name = "public.dissemination_migrationinspectionrecord"
        return (
            f"{table_name}.{audit_year}",
            ReplicationStream(
                object=f"public-data/gsa/migration/{audit_year}-inspectionrecord.csv",
                sql=self.query.format(audit_year=audit_year),
                mode="full-refresh",
                target_options={"format": "csv"},
            ),
        )

    def generate_stream_invalidaudit(self, audit_year):
        table_name = "public.dissemination_invalidauditrecord"
        return (
            f"{table_name}.{audit_year}",
            ReplicationStream(
                object=f"public-data/gsa/migration/{audit_year}-invalidauditrecord.csv",
                sql=self.query.format(audit_year=audit_year),
                mode="full-refresh",
                target_options={"format": "csv"},
            ),
        )


STREAM_GENERATORS = [
    StreamGenerator(
        query=(
            "select * from dissemination_migrationinspectionrecord "
            "where audit_year='{audit_year}' and "
            "report_id in (select report_id from dissemination_general where audit_year='{audit_year}' and is_public='True')"
        ),
    ),
]

STREAM_GENERATORS_INVALID_AUDIT = [
    StreamGenerator(
        query=(
            "select * from dissemination_invalidauditrecord "
            "where audit_year='{audit_year}' and "
            "report_id in (select report_id from dissemination_general where audit_year='{audit_year}' and is_public='True')"
        ),
    ),
]


def _run_data_export(year):
    logger.info(
        f"Begin exporting data from dissemination migrationinspectionrecord and invalidauditrecord tables for year={year}"
    )

    streams = {}

    for stream_generator in STREAM_GENERATORS:
        streams.update([stream_generator.generate_stream_inspection(year)])

    for stream_generator in STREAM_GENERATORS_INVALID_AUDIT:
        streams.update([stream_generator.generate_stream_invalidaudit(year)])

    replication = Replication(
        source="FAC_DB",
        target="BULK_DATA_EXPORT",
        streams=streams,
        defaults=DEFAULT_OPTIONS,
        env=dict(
            FAC_DB=FAC_DB_URL, BULK_DATA_EXPORT=S3_CONNECTION, SLING_ALLOW_EMPTY="TRUE"
        ),
        debug=settings.DEBUG,
    )
    logger.info(f"Exporting {len(streams)} streams")
    replication.run()
    logger.info(
        "Successfully exported data from dissemination migrationinspectionrecord and invalidauditrecord tables"
    )


class Command(BaseCommand):
    help = """
    Export dissemination migrationinspectionrecord and invalidauditrecord data for audit years >=2016 and <=2022.
    Default is current year.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            help="Year(>=2016 and <=2022)",
            type=str,
            default=datetime.today().year,
        )

    def is_year_invalid(self, year):
        return int(year) < 2016 or int(year) > 2022

    def handle(self, *args, **options):
        year = options.get("year")
        if self.is_year_invalid(year):
            print(f"Invalid year {year}.  Expecting >=2016 and <=2022")
            return

        year = int(year)

        try:
            _run_data_export(year)
        except Exception as ex:
            logger.error(
                "An error occurred while exporting data from dissemination migrationinspectionrecord and invalidauditrecord tables",
                exc_info=ex,
            )
            raise CommandError(
                "Error while exporting data from dissemination migrationinspectionrecord and invalidauditrecord tables"
            )
