from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class Finding(models.Model):
    """A finding from the audit. References FederalAward and FindingText"""

    HASH_FIELDS = [
        "report_id",
        "federal_agency_prefix",
        "federal_award_extension",
        "aln",
        "award_reference",
        "reference_number",
        "type_requirement",
        "is_modified_opinion",
        "is_other_findings",
        "is_material_weakness",
        "is_significant_deficiency",
        "is_other_matters",
        "is_questioned_costs",
        "is_repeat_finding",
        "prior_finding_ref_numbers",
    ]

    award_reference = models.TextField(
        "Order that the award line was reported in Award",
    )
    reference_number = models.TextField(
        "Findings Reference Numbers",
        help_text=docs.finding_ref_nums_findings,
    )
    is_material_weakness = models.TextField(
        "Material Weakness finding",
        help_text=docs.material_weakness_findings,
    )
    is_modified_opinion = models.TextField(
        "Modified Opinion finding", help_text=docs.modified_opinion
    )
    is_other_findings = models.TextField(
        "Other findings", help_text=docs.other_findings
    )
    is_other_matters = models.TextField(
        "Other non-compliance", help_text=docs.other_non_compliance
    )
    is_questioned_costs = models.TextField(
        "Questioned Costs", help_text=docs.questioned_costs_findings
    )
    is_repeat_finding = models.TextField(
        "Indicates whether or not the audit finding was a repeat of an audit finding in the immediate prior audit",
        help_text=docs.repeat_finding,
    )
    is_significant_deficiency = models.TextField(
        "Significant Deficiency finding",
        help_text=docs.significant_deficiency_findings,
    )
    prior_finding_ref_numbers = models.TextField(
        "Audit finding reference numbers from the immediate prior audit",
        help_text=docs.prior_finding_ref_nums,
    )
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    # each element in the list is a FK to Finding
    type_requirement = models.TextField(
        "Type Requirement Failure",
        help_text=docs.type_requirement_findings,
    )
    hash = models.CharField(
        help_text="A hash of the row",
        blank=True,
        null=True,
    )
