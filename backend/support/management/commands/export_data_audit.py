import os
import logging
import support.export_audit_sql as export_audit_sql

from config import settings
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from sling import Replication, ReplicationStream

from support.decorators import newrelic_timing_metric

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
    def __init__(self, table_name, friendly_name, query=None):
        self.table_name = table_name
        self.friendly_name = friendly_name
        self.query = query

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
        table_name="general_information",
        query=export_audit_sql.select_general_information,
    ),
    StreamGenerator(
        friendly_name="AdditionalEIN",
        table_name="additional_eins",
        query=export_audit_sql.select_additional_eins,
    ),
    StreamGenerator(
        friendly_name="AdditionalUEI",
        table_name="additional_ueis",
        query=export_audit_sql.select_additional_ueis,
    ),
    StreamGenerator(
        friendly_name="CorrectiveActionPlans",
        table_name="corrective_action_plan",
        query=export_audit_sql.select_corrective_action_plans,
    ),
    StreamGenerator(
        friendly_name="FederalAward",
        table_name="federal_awards",
        query=export_audit_sql.select_federal_awards,
    ),
    StreamGenerator(
        friendly_name="Finding",
        table_name="findings_uniform_guidance",
        query=export_audit_sql.select_findings,
    ),
    StreamGenerator(
        friendly_name="FindingText",
        table_name="findings_text",
        query=export_audit_sql.select_findings_text,
    ),
    StreamGenerator(
        friendly_name="Note",
        table_name="notes_to_sefa",
        query=export_audit_sql.select_notes_to_sefa,
    ),
    StreamGenerator(
        friendly_name="PassThrough",
        table_name="passthrough",
        query=export_audit_sql.select_passthrough,
    ),
    StreamGenerator(
        friendly_name="SecondaryAuditor",
        table_name="secondary_auditors",
        query=export_audit_sql.select_secondary_auditors,
    ),
]


@newrelic_timing_metric("data_export")
def _run_data_export():
    logger.info("Begin exporting data from audit table")
    # We may want to consider instead of hardcoding 2016 only export the past X years.
    # This will only export data that exists, so doing +2 just incase some data is in early
    years = range(2016, datetime.today().year + 2)
    streams = {}
    for year in years:
        for stream_generator in STREAM_GENERATORS:
            streams.update([stream_generator.generate_stream(year)])

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
    def handle(self, *args, **kwargs):
        try:
            _run_data_export()
        except Exception as ex:
            logger.error(
                "An error occurred while exporting data from audit table", exc_info=ex
            )
            raise CommandError("Error while exporting data from audit table")
