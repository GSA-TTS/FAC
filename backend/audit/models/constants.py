from django.utils.translation import gettext_lazy as _
from collections import namedtuple as nt


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
)


class AuditType:
    SINGLE_AUDIT = "single_audit"
    PROGRAM_SPECIFIC = "program_specific"


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
