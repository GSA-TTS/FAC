from dissemination.api_versions import exec_sql_at_path

SQL_PATH = "curation/sql"


class CurationTracking:
    """
    Wraps "audit-tracking" around any block of logic.
    This guarantees that any DB writes within the block will be recorded.
    """

    initialized = False

    # On first entry, initialize the curation indexes and functions. It should always be setup in
    # online environments, but it's not guaranteed. This also ensures a duplicate initialization
    # when redeploying online, to ensure any changes are brought through.
    def __enter__(self):
        if not self.initialized:
            init_audit_curation()
            self.initialized = True

        enable_audit_curation()
        return None

    def __exit__(self, exc_type, exc_value, tb):
        disable_audit_curation()


def init_audit_curation():
    exec_sql_at_path(SQL_PATH, "init_curation_auditing.sql")


def enable_audit_curation():
    exec_sql_at_path(SQL_PATH, "enable_curation_auditing.sql")


def disable_audit_curation():
    exec_sql_at_path(SQL_PATH, "disable_curation_auditing.sql")
