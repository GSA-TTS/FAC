import copy

from django.db import models

from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    Passthrough,
)

# Used to import fields from other models to reduce code duplication
fields_to_import = [
    (
        General,
        [
            "auditee_certify_name",
            "auditee_certify_title",
            "auditor_certify_name",
            "auditor_certify_title",
            "auditee_contact_name",
            "auditee_email",
            "auditee_name",
            "auditee_phone",
            "auditee_contact_title",
            "auditee_address_line_1",
            "auditee_city",
            "auditee_state",
            "auditee_ein",
            "auditee_uei",
            "is_additional_ueis",
            "auditee_zip",
            "auditor_phone",
            "auditor_state",
            "auditor_city",
            "auditor_contact_title",
            "auditor_address_line_1",
            "auditor_zip",
            "auditor_country",
            "auditor_contact_name",
            "auditor_email",
            "auditor_firm_name",
            "auditor_foreign_address",
            "auditor_ein",
            "resubmission_version",
            "resubmission_status",
            "cognizant_agency",
            "oversight_agency",
            "date_created",
            "ready_for_certification_date",
            "auditor_certified_date",
            "auditee_certified_date",
            "submitted_date",
            "fac_accepted_date",
            "fy_end_date",
            "fy_start_date",
            "audit_year",
            "audit_type",
            "gaap_results",
            "sp_framework_basis",
            "is_sp_framework_required",
            "sp_framework_opinions",
            "is_going_concern_included",
            "is_internal_control_deficiency_disclosed",
            "is_internal_control_material_weakness_disclosed",
            "is_material_noncompliance_disclosed",
            "is_aicpa_audit_guide_included",
            "dollar_threshold",
            "is_low_risk_auditee",
            "agencies_with_prior_findings",
            "entity_type",
            "number_months",
            "audit_period_covered",
            "total_amount_expended",
            "type_audit_code",
            "is_public",
            "data_source",
        ],
    ),
    (
        FederalAward,
        [
            "additional_award_identification",
            "amount_expended",
            "award_reference",
            "cluster_name",
            "cluster_total",
            "federal_agency_prefix",
            "federal_award_extension",
            "federal_program_name",
            "federal_program_total",
            "findings_count",
            "is_direct",
            "is_loan",
            "is_major",
            "is_passthrough_award",
            "loan_balance",
            "audit_report_type",
            "other_cluster_name",
            "passthrough_amount",
            "state_cluster_name",
        ],
    ),
    (
        Finding,
        [
            "reference_number",
            "is_material_weakness",
            "is_modified_opinion",
            "is_other_findings",
            "is_other_matters",
            "is_questioned_costs",
            "is_repeat_finding",
            "is_significant_deficiency",
            "prior_finding_ref_numbers",
            "type_requirement",
        ],
    ),
    (
        Passthrough,
        [
            "passthrough_id",
            "passthrough_name",
        ],
    ),
]


class Unified(models.Model):
    """
    Represents the 'dissemination_unified' table.
    This is a selective-JOINing of federal general info, awards, findings, and
    passthroughs.
    """
    report_id = models.ForeignKey(
        "General",
        help_text=REPORT_ID_FK_HELP_TEXT,
        on_delete=models.CASCADE,
        to_field="report_id",
        db_column="report_id",
    )
    aln = models.TextField(
        "2-char agency code concatenated to 3-digit program extn",
    )


# Adds fields we need from other models
for model_class, field_names in fields_to_import:
    for field_name in field_names:
        source_field = model_class._meta.get_field(field_name)

        # Deepcopy it so it loses its attachment to the original model
        new_field = copy.deepcopy(source_field)

        # creation_counter is used to maintain field ordering in the DB
        # Setting it manually since the imported fields would have clashes
        new_field.creation_counter = models.Field.creation_counter
        models.Field.creation_counter += 1

        Unified.add_to_class(field_name, new_field)
