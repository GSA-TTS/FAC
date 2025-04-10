import os
import logging
from support.export_audit_streams import (
    STREAM_GENERATORS,
    STREAM_GENERATORS_ALL,
    STREAM_GENERATORS_FEDERAL_YEAR,
)

from config import settings
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from support.decorators import newrelic_timing_metric
from sling import Replication

logger = logging.getLogger(__name__)

S3_CONNECTION = f"""{{
            "type": "s3",
            "bucket": "{settings.AWS_PRIVATE_STORAGE_BUCKET_NAME}",
            "access_key_id": "{settings.AWS_PRIVATE_ACCESS_KEY_ID}",
            "secret_access_key": "{settings.AWS_PRIVATE_SECRET_ACCESS_KEY}",
            "endpoint": "{settings.AWS_S3_ENDPOINT_URL}",
            "region": "{settings.AWS_S3_PRIVATE_REGION_NAME}"
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


@newrelic_timing_metric("data_export")
def _run_data_export(year):
    logger.info(f"Begin exporting data from audit table for year={year}")

    streams = {}
    if year == "all":
        for stream_generator in STREAM_GENERATORS_ALL:
            streams.update([stream_generator.generate_stream_all()])
    else:
        for stream_generator in STREAM_GENERATORS:
            streams.update([stream_generator.generate_stream(year)])
        for stream_generator in STREAM_GENERATORS_FEDERAL_YEAR:
            streams.update([stream_generator.generate_fed_year_stream(year)])

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
    logger.info("Successfully exported data from audit table")


class Command(BaseCommand):
    help = """
    Export dissemination data for audit years >=2016/all.
    Default is current year.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            help="Year(>=2016 or all)",
            type=str,
            default=datetime.today().year,
        )

    def is_year_invalid(self, year):
        if year != "all":
            return int(year) < 2016
        else:
            return False

    def handle(self, *args, **options):
        year = options.get("year")
        if self.is_year_invalid(year):
            print(f"Invalid year {year}.  Expecting >=2016 / all")
            return

        if year != "all":
            year = int(year)

        try:
            _run_data_export(year)
        except Exception as ex:
            logger.error(
                "An error occurred while exporting data from audit table", exc_info=ex
            )
            raise CommandError("Error while exporting data from audit table")
