from .access import Access
from .deleted_access import DeletedAccess
from .models import (
    ExcelFile,
    GeneralInformationMixin,
    LateChangeError,
    SingleAuditChecklist,
    SingleAuditChecklistManager,
    SingleAuditReportFile,
    User,
    excel_file_path,
    generate_sac_report_id,
    single_audit_report_path,
    MigrationChangeLogs,
)
from .submission_event import SubmissionEvent

# In case we want to iterate through all the models for some reason:
_models = [
    Access,
    DeletedAccess,
    ExcelFile,
    GeneralInformationMixin,
    SubmissionEvent,
    LateChangeError,
    SingleAuditChecklist,
    SingleAuditChecklistManager,
    SingleAuditReportFile,
    User,
    MigrationChangeLogs,
]
_functions = [
    excel_file_path,
    generate_sac_report_id,
    single_audit_report_path,
]
