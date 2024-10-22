from dissemination import api_versions

SQL_PATH = "curation/sql"


class CurationTracking:
    """
    Wraps "audit-tracking" around any block of logic.
    This guarantees that any DB writes within the block will be recorded.
    """

    def __enter__(self):
        enable_audit_curation()
        return None

    def __exit__(self, exc_type, exc_value, tb):
        disable_audit_curation()


def init_audit_curation():
    api_versions.exec_sql_at_path(SQL_PATH, "init_curation_auditing.sql")


def enable_audit_curation():
    api_versions.exec_sql_at_path(SQL_PATH, "enable_curation_auditing.sql")


def disable_audit_curation():
    api_versions.exec_sql_at_path(SQL_PATH, "disable_curation_auditing.sql")
