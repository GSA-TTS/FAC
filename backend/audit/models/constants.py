from django.utils.translation import gettext_lazy as _
from collections import namedtuple as nt

DATA_SOURCE_GSAFAC = "GSAFAC"
DATA_SOURCE_CENSUS = "CENSUS"
VALID_DATA_SOURCES = [DATA_SOURCE_GSAFAC, DATA_SOURCE_CENSUS]


class ORGANIZATION_TYPE:
    STATE = "state"
    LOCAL = "local"
    TRIBAL = "tribal"
    HIGHER_ED = "higher-ed"
    NON_PROFIT = "non-profit"
    UNKNOWN = "unknown"
    NONE = "none"


class STATUS:
    """
    The possible states of a submission.
    """

    IN_PROGRESS = "in_progress"
    READY_FOR_CERTIFICATION = "ready_for_certification"
    AUDITOR_CERTIFIED = "auditor_certified"
    AUDITEE_CERTIFIED = "auditee_certified"
    CERTIFIED = "certified"
    SUBMITTED = "submitted"
    DISSEMINATED = "disseminated"
    RESUBMITTED = "resubmitted"
    FLAGGED_FOR_REMOVAL = "flagged_for_removal"


STATUS_CHOICES = (
    (STATUS.IN_PROGRESS, "In Progress"),
    (STATUS.FLAGGED_FOR_REMOVAL, "Flagged for Removal"),
    (STATUS.READY_FOR_CERTIFICATION, "Ready for Certification"),
    (STATUS.AUDITOR_CERTIFIED, "Auditor Certified"),
    (STATUS.AUDITEE_CERTIFIED, "Auditee Certified"),
    (STATUS.CERTIFIED, "Certified"),
    (STATUS.SUBMITTED, "Submitted"),
    (STATUS.DISSEMINATED, "Disseminated"),
    (STATUS.RESUBMITTED, "Resubmitted"),
)


class RESUBMISSION_STATUS:
    ORIGINAL = "original_submission"
    MOST_RECENT = "most_recent"
    DEPRECATED = "deprecated_via_resubmission"


RESUBMISSION_STATUS_CHOICES = (
    (RESUBMISSION_STATUS.ORIGINAL, "Original Submission"),
    (RESUBMISSION_STATUS.MOST_RECENT, "Most Recent"),
    (RESUBMISSION_STATUS.DEPRECATED, "Deprecated via Resubmission"),
)


class EventType:
    ACCESS_GRANTED = "access-granted"
    ADDITIONAL_EINS_UPDATED = "additional-eins-updated"
    ADDITIONAL_EINS_DELETED = "additional-eins-deleted"
    ADDITIONAL_UEIS_UPDATED = "additional-ueis-updated"
    ADDITIONAL_UEIS_DELETED = "additional-ueis-deleted"
    AUDIT_INFORMATION_UPDATED = "audit-information-updated"
    AUDIT_REPORT_PDF_UPDATED = "audit-report-pdf-updated"
    AUDITEE_CERTIFICATION_COMPLETED = "auditee-certification-completed"
    AUDITOR_CERTIFICATION_COMPLETED = "auditor-certification-completed"
    CORRECTIVE_ACTION_PLAN_UPDATED = "corrective-action-plan-updated"
    CORRECTIVE_ACTION_PLAN_DELETED = "corrective-action-plan-deleted"
    CREATED = "created"
    FEDERAL_AWARDS_UPDATED = "federal-awards-updated"
    FEDERAL_AWARDS_AUDIT_FINDINGS_UPDATED = "federal-awards-audit-findings-updated"
    FEDERAL_AWARDS_AUDIT_FINDINGS_DELETED = "federal-awards-audit-findings-deleted"
    FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED = (
        "federal-awards-audit-findings-text-updated"
    )
    FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_DELETED = (
        "federal-awards-audit-findings-text-deleted"
    )
    FINDINGS_UNIFORM_GUIDANCE_UPDATED = "findings-uniform-guidance-updated"
    FINDINGS_UNIFORM_GUIDANCE_DELETED = "findings-uniform-guidance-deleted"
    GENERAL_INFORMATION_UPDATED = "general-information-updated"
    LOCKED_FOR_CERTIFICATION = "locked-for-certification"
    UNLOCKED_AFTER_CERTIFICATION = "unlocked-after-certification"
    NOTES_TO_SEFA_UPDATED = "notes-to-sefa-updated"
    SECONDARY_AUDITORS_UPDATED = "secondary-auditors-updated"
    SECONDARY_AUDITORS_DELETED = "secondary-auditors-deleted"
    SUBMITTED = "submitted"
    DISSEMINATED = "disseminated"
    TRIBAL_CONSENT_UPDATED = "tribal-consent-updated"
    FLAGGED_SUBMISSION_FOR_REMOVAL = "flagged-submission-for-removal"
    CANCEL_REMOVAL_FLAG = "cancel-removal-flag"
    SOURCE_OF_TRUTH_MIGRATION = "sot-migration"


EVENT_TYPES = (
    (EventType.ACCESS_GRANTED, _("Access granted")),
    (EventType.ADDITIONAL_EINS_UPDATED, _("Additional EINs updated")),
    (EventType.ADDITIONAL_EINS_DELETED, _("Additional EINs deleted")),
    (EventType.ADDITIONAL_UEIS_UPDATED, _("Additional UEIs updated")),
    (EventType.ADDITIONAL_UEIS_DELETED, _("Additional UEIs deleted")),
    (EventType.AUDIT_INFORMATION_UPDATED, _("Audit information updated")),
    (EventType.AUDIT_REPORT_PDF_UPDATED, _("Audit report PDF updated")),
    (
        EventType.AUDITEE_CERTIFICATION_COMPLETED,
        _("Auditee certification completed"),
    ),
    (
        EventType.AUDITOR_CERTIFICATION_COMPLETED,
        _("Auditor certification completed"),
    ),
    (EventType.CORRECTIVE_ACTION_PLAN_UPDATED, _("Corrective action plan updated")),
    (EventType.CORRECTIVE_ACTION_PLAN_DELETED, _("Corrective action plan deleted")),
    (EventType.CREATED, _("Created")),
    (EventType.FEDERAL_AWARDS_UPDATED, _("Federal awards updated")),
    (
        EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_UPDATED,
        _("Federal awards audit findings updated"),
    ),
    (
        EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_DELETED,
        _("Federal awards audit findings deleted"),
    ),
    (
        EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED,
        _("Federal awards audit findings text updated"),
    ),
    (
        EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_DELETED,
        _("Federal awards audit findings text deleted"),
    ),
    (
        EventType.FINDINGS_UNIFORM_GUIDANCE_UPDATED,
        _("Findings uniform guidance updated"),
    ),
    (
        EventType.FINDINGS_UNIFORM_GUIDANCE_DELETED,
        _("Findings uniform guidance deleted"),
    ),
    (EventType.GENERAL_INFORMATION_UPDATED, _("General information updated")),
    (EventType.LOCKED_FOR_CERTIFICATION, _("Locked for certification")),
    (EventType.UNLOCKED_AFTER_CERTIFICATION, _("Unlocked after certification")),
    (EventType.NOTES_TO_SEFA_UPDATED, _("Notes to SEFA updated")),
    (EventType.SECONDARY_AUDITORS_UPDATED, _("Secondary auditors updated")),
    (EventType.SECONDARY_AUDITORS_DELETED, _("Secondary auditors deleted")),
    (EventType.SUBMITTED, _("Submitted to the FAC for processing")),
    (EventType.DISSEMINATED, _("Copied to dissemination tables")),
    (EventType.TRIBAL_CONSENT_UPDATED, _("Tribal audit consent updated")),
    (
        EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
        _("Flagged submission for removal"),
    ),
    (EventType.CANCEL_REMOVAL_FLAG, _("Cancel removal flag")),
    (EventType.SOURCE_OF_TRUTH_MIGRATION, _("Source of Truth Migration")),
)


class AuditType:
    SINGLE_AUDIT = "single-audit"
    PROGRAM_SPECIFIC = "program-specific"


AUDIT_TYPE_CODES = (
    (AuditType.SINGLE_AUDIT, _("Single Audit")),
    (AuditType.PROGRAM_SPECIFIC, _("Program-Specific Audit")),
)


class FindingsBitmask:
    MODIFIED_OPINION = 1  # 0b0000001
    OTHER_FINDINGS = 2  # 0b0000010
    MATERIAL_WEAKNESS = 4  # 0b0000100
    SIGNIFICANT_DEFICIENCY = 8  # 0b0001000
    OTHER_MATTERS = 16  # 0b0010000
    QUESTIONED_COSTS = 32  # 0b0100000
    REPEAT_FINDING = 64  # 0b1000000
    ALL = 127  # 0b1111111


FindingsFieldBitmask = nt("FindingsFieldBitmask", ["field", "search_param", "mask"])
FINDINGS_FIELD_TO_BITMASK = [
    FindingsFieldBitmask(
        field="modified_opinion",
        search_param="is_modified_opinion",
        mask=FindingsBitmask.MODIFIED_OPINION,
    ),
    FindingsFieldBitmask(
        field="other_findings",
        search_param="is_other_findings",
        mask=FindingsBitmask.OTHER_FINDINGS,
    ),
    FindingsFieldBitmask(
        field="material_weakness",
        search_param="is_material_weakness",
        mask=FindingsBitmask.MATERIAL_WEAKNESS,
    ),
    FindingsFieldBitmask(
        field="significant_deficiency",
        search_param="is_significant_deficiency",
        mask=FindingsBitmask.SIGNIFICANT_DEFICIENCY,
    ),
    FindingsFieldBitmask(
        field="other_matters",
        search_param="is_other_matters",
        mask=FindingsBitmask.OTHER_MATTERS,
    ),
    FindingsFieldBitmask(
        field="questioned_costs",
        search_param="is_questioned_costs",
        mask=FindingsBitmask.QUESTIONED_COSTS,
    ),
    # This is a special case handled by dissemination, but works using this in search
    FindingsFieldBitmask(
        field="_blank_",
        search_param="is_repeat_finding",
        mask=FindingsBitmask.REPEAT_FINDING,
    ),
]

SAC_SEQUENCE_ID = "public.audit_singleauditchecklist_id_seq"
AUDIT_SEQUENCE_ID = "public.audit_audit_id_seq"
