from dissemination import api_versions

SQL_PATH = "curation/sql"

def init_audit_curation():
    api_versions.exec_sql_at_path(SQL_PATH, "init_curation_auditing.sql")

def enable_audit_curation():
    api_versions.exec_sql_at_path(SQL_PATH, "enable_curation_auditing.sql")

def disable_audit_curation():
    api_versions.exec_sql_at_path(SQL_PATH, "disable_curation_auditing.sql")

