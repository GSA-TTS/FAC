import support.export_audit_sql as export_audit_sql
from sling import ReplicationStream

API_VERSION = "api_v1_1_0"


class StreamGenerator:
    def __init__(self, query=None):
        self.query = query

    def generate_stream(self, audit_year):
        table_name = (self.query.split(".")[1]).split(" ")[0]
        return (
            f"{table_name}.{audit_year}",
            ReplicationStream(
                object=f"public-data/gsa/audit-year/{audit_year}-ay-{table_name}.csv",
                sql=self.query.format(api_version=API_VERSION, audit_year=audit_year),
                mode="full-refresh",
                target_options={"format": "csv"},
            ),
        )

    def generate_stream_all(self):
        table_name = (self.query.split(".")[1]).split(" ")[0]
        return (
            f"{table_name}",
            ReplicationStream(
                object=f"public-data/gsa/full/{table_name}.csv",
                sql=self.query.format(api_version=API_VERSION),
                mode="full-refresh",
                target_options={"format": "csv"},
            ),
        )

    def generate_fed_year_stream(self, audit_year):
        table_name = (self.query.split(".")[1]).split(" ")[0]
        prev_audit_year = audit_year - 1
        fac_accepted_date_start = str(prev_audit_year) + "-10-31"
        fac_accepted_date_end = str(audit_year) + "-09-30"
        return (
            f"{table_name}_Federal_year.{audit_year}",
            ReplicationStream(
                object=f"public-data/gsa/federal-fiscal-year/{audit_year}-ffy-{table_name}.csv",
                sql=self.query.format(
                    api_version=API_VERSION,
                    fac_accepted_date_start=fac_accepted_date_start,
                    fac_accepted_date_end=fac_accepted_date_end,
                ),
                mode="full-refresh",
                target_options={"format": "csv"},
            ),
        )


STREAM_GENERATORS = [
    StreamGenerator(
        query=export_audit_sql.select_general_information,
    ),
    StreamGenerator(
        query=export_audit_sql.select_additional_eins,
    ),
    StreamGenerator(
        query=export_audit_sql.select_additional_ueis,
    ),
    StreamGenerator(
        query=export_audit_sql.select_corrective_action_plans,
    ),
    StreamGenerator(
        query=export_audit_sql.select_federal_awards,
    ),
    StreamGenerator(
        query=export_audit_sql.select_findings,
    ),
    StreamGenerator(
        query=export_audit_sql.select_findings_text,
    ),
    StreamGenerator(
        query=export_audit_sql.select_notes_to_sefa,
    ),
    StreamGenerator(
        query=export_audit_sql.select_passthrough,
    ),
    StreamGenerator(
        query=export_audit_sql.select_secondary_auditors,
    ),
]


STREAM_GENERATORS_ALL = [
    StreamGenerator(
        query=export_audit_sql.select_all_general_information,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_additional_eins,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_additional_ueis,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_corrective_action_plans,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_federal_awards,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_findings,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_findings_text,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_notes_to_sefa,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_passthrough,
    ),
    StreamGenerator(
        query=export_audit_sql.select_all_secondary_auditors,
    ),
]


STREAM_GENERATORS_FEDERAL_YEAR = [
    StreamGenerator(
        query=export_audit_sql.select_fed_year_general_information,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_additional_eins,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_additional_ueis,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_corrective_action_plans,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_federal_awards,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_findings,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_findings_text,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_notes_to_sefa,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_passthrough,
    ),
    StreamGenerator(
        query=export_audit_sql.select_fed_year_secondary_auditors,
    ),
]
