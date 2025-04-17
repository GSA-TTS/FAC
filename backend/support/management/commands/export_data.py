import os
import logging

from config import settings
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sling import Replication, ReplicationStream

from support.decorators import newrelic_timing_metric
from dissemination.summary_reports import restricted_model_names

logger = logging.getLogger(__name__)

S3_CONNECTION = f"""{{
            "type": "s3",
            "bucket": "{settings.AWS_PRIVATE_STORAGE_BUCKET_NAME}",
            "access_key_id": "{settings.AWS_PRIVATE_ACCESS_KEY_ID}",
            "secret_access_key": "{settings.AWS_PRIVATE_SECRET_ACCESS_KEY}",
            "endpoint": "{settings.AWS_S3_ENDPOINT_URL}"
         }}
    """
DB_URL = os.environ.get("DATABASE_URL")
FAC_DB_URL = (
    f"{DB_URL}?sslmode=disable" if settings.ENVIRONMENT in ["LOCAL", "TEST"] else DB_URL
)
DEFAULT_OPTIONS = {
    "target_options": {
        "format": "csv",
        "compression": "gzip",
        "file_max_rows": 0,
    }
}


class StreamGenerator:
    EXCLUDE_NONPUBLIC_QUERY = (
        "select * from {table_name} where report_id in ("
        " select dg.report_id from public.dissemination_general dg"
        " where dg.audit_year = '{audit_year}' and dg.is_public = 'true' )"
    )

    UNRESTRICTED_QUERY = (
        "select * from {table_name} where report_id in ("
        " select dg.report_id from public.dissemination_general dg"
        " where dg.audit_year = '{audit_year}')"
    )

    def __init__(self, table_name, friendly_name, query_override=None):
        self.table_name = table_name
        self.friendly_name = friendly_name

        restricted_tables = [
            "dissemination_" + model for model in restricted_model_names
        ]
        default_query = (
            self.EXCLUDE_NONPUBLIC_QUERY
            if table_name in restricted_tables
            else self.UNRESTRICTED_QUERY
        )
        self.query = query_override or default_query

    def generate_stream(self, audit_year):
        return (
            f"{self.table_name}.{audit_year}",
            ReplicationStream(
                object=f"bulk_export/{{MM}}/{audit_year}_{self.friendly_name}.csv",
                sql=self.query.format(
                    table_name=self.table_name, audit_year=audit_year
                ),
                mode="full-refresh",
                target_options={"format": "csv"},
            ),
        )


STREAM_GENERATORS = [
    StreamGenerator(
        friendly_name="General",
        table_name="dissemination_general",
        query_override="select * from dissemination_general where audit_year = '{audit_year}'",
    ),
    StreamGenerator(
        friendly_name="AdditionalEIN", table_name="dissemination_additionalein"
    ),
    StreamGenerator(
        friendly_name="AdditionalUEI", table_name="dissemination_additionaluei"
    ),
    StreamGenerator(
        friendly_name="CorrectiveActionPlans", table_name="dissemination_captext"
    ),
    StreamGenerator(
        friendly_name="FederalAward", table_name="dissemination_federalaward"
    ),
    StreamGenerator(friendly_name="Finding", table_name="dissemination_finding"),
    StreamGenerator(
        friendly_name="FindingText", table_name="dissemination_findingtext"
    ),
    StreamGenerator(friendly_name="Note", table_name="dissemination_note"),
    StreamGenerator(
        friendly_name="PassThrough", table_name="dissemination_passthrough"
    ),
    StreamGenerator(
        friendly_name="SecondaryAuditor", table_name="dissemination_secondaryauditor"
    ),
]


@newrelic_timing_metric("data_export")
def _run_data_export():
    logger.info("Begin exporting data")
    # We may want to consider instead of hardcoding 2016 only export the past X years.
    # This will only export data that exists, so doing +2 just incase some data is in early
    years = range(2016, datetime.today().year + 2)
    streams = {}
    for stream_generator in STREAM_GENERATORS:
        for year in years:
            streams.update([stream_generator.generate_stream(year)])

    replication = Replication(
        source="FAC_DB",
        target="BULK_DATA_EXPORT",
        streams=streams,
        defaults=DEFAULT_OPTIONS,
        env=dict(FAC_DB=FAC_DB_URL, BULK_DATA_EXPORT=S3_CONNECTION),
        debug=settings.DEBUG,
    )
    logger.info(f"Exporting {len(streams)} streams")
    replication.run()
    logger.info("Successfully exported data")


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            _run_data_export()
        except Exception as ex:
            logger.error("An error occurred while exporting data", exc_info=ex)
            raise CommandError("Error while exporting data")
