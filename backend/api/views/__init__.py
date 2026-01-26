from api.views.access import (
    AccessAndSubmissionView,
    AccessListView,
    access_and_submission_check,
)
from api.views.audit import (
    SingleAuditChecklistView,
    SubmissionsView,
    AuditView,
    AuditAwardsView,
    AuditSubmissionsView,
)
from api.views.auditee import AuditeeInfoView, auditee_info_check
from api.views.common import SchemaView, Sprite
from api.views.eligibility import EligibilityFormView, eligibility_check
from api.views.uei import UEIValidationFormView

views = [
    AccessAndSubmissionView,
    AccessListView,
    AuditAwardsView,
    AuditView,
    AuditeeInfoView,
    AuditSubmissionsView,
    EligibilityFormView,
    SchemaView,
    SingleAuditChecklistView,
    Sprite,
    SubmissionsView,
    UEIValidationFormView,
]

functions = [access_and_submission_check, auditee_info_check, eligibility_check]
