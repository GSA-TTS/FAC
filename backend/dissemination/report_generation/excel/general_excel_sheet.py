from audit.models import History
from audit.models.constants import EventType
from audit.utils import Util
from dissemination.report_generation.excel.excel_sheet import ExcelSheet


def _get_entry(audit):
    if not audit or not audit.audit:
        return [[]]
    general_information = audit.audit.get("general_information", None)
    if not general_information:
        return [[]]

    auditee_certification = audit.audit.get("auditee_certification", {})
    auditor_certification = audit.audit.get("auditor_certification", {})
    audit_information = audit.audit.get("audit_information", {})

    events = (
        EventType.AUDITEE_CERTIFICATION_COMPLETED,
        EventType.AUDITOR_CERTIFICATION_COMPLETED,
        EventType.LOCKED_FOR_CERTIFICATION,
        EventType.SUBMITTED,
    )

    audit_history = History.objects.filter(
        report_id=audit.report_id, event__in=events
    ).order_by("updated_at")
    history_dict = {
        history.event: Util.format_date(history.updated_at) for history in audit_history
    }

    return [
        [
            audit.report_id,
            audit.audit_year,
            audit.audit.get("federal_awards").get("total_amount_expended"),
            general_information.get("user_provided_organization_type"),  # entity_type
            general_information.get("auditee_fiscal_period_start"),  # fy_start_date
            general_information.get("auditee_fiscal_period_end"),  # fy_start_date
            general_information.get("audit_type"),
            general_information.get("audit_period_covered"),
            general_information.get("audit_period_other_months"),  # number_months
            general_information.get("auditee_uei"),
            general_information.get("ein"),  # auditee_ein
            general_information.get("auditee_name"),
            general_information.get("auditee_address_line_1"),
            general_information.get("auditee_city"),
            general_information.get("auditee_state"),
            general_information.get("auditee_zip"),
            general_information.get("auditee_contact_name"),
            general_information.get("auditee_contact_title"),
            general_information.get("auditee_phone"),
            general_information.get("auditee_email"),
            history_dict.get(
                EventType.AUDITEE_CERTIFICATION_COMPLETED
            ),  # auditee_certified_date
            auditee_certification.get("auditee_signature", {}).get(
                "auditee_name"
            ),  # auditee_certify_name
            auditee_certification.get("auditee_signature", {}).get(
                "auditee_title"
            ),  # auditee_certify_title
            general_information.get("auditor_ein"),
            general_information.get("auditor_firm_name"),
            general_information.get("auditor_address_line_1"),
            general_information.get("auditor_city"),
            general_information.get("auditor_state"),
            general_information.get("auditor_zip"),
            general_information.get("auditor_country"),
            general_information.get("auditor_contact_name"),
            general_information.get("auditor_contact_title"),
            general_information.get("auditor_phone"),
            general_information.get("auditor_email"),
            general_information.get(
                "auditor_international_address"
            ),  # auditor_foreign_address
            history_dict.get(
                EventType.AUDITOR_CERTIFICATION_COMPLETED
            ),  # auditor_certified_date
            auditor_certification.get("auditor_signature", {}).get(
                "auditor_name"
            ),  # auditor_certify_name
            auditor_certification.get("auditor_signature", {}).get(
                "auditor_title"
            ),  # auditor_certify_title
            audit.cognizant_agency,
            audit.oversight_agency,
            "UG",  # type_audit_code
            Util.json_array_to_str(audit_information.get("sp_framework_basis", [])),
            Util.optional_bool(audit_information.get("is_sp_framework_required", None)),
            Util.bool_to_yes_no(
                audit_information.get("is_going_concern_included", False)
            ),
            Util.bool_to_yes_no(
                audit_information.get("is_internal_control_deficiency_disclosed", False)
            ),
            Util.bool_to_yes_no(
                audit_information.get(
                    "is_internal_control_material_weakness_disclosed", False
                )
            ),
            Util.bool_to_yes_no(
                audit_information.get("is_material_noncompliance_disclosed", False)
            ),
            Util.json_array_to_str(audit_information.get("gaap_results", [])),
            Util.bool_to_yes_no(
                audit_information.get("is_aicpa_audit_guide_included", False)
            ),
            Util.json_array_to_str(audit_information.get("sp_framework_opinions", [])),
            Util.json_array_to_str(
                audit_information.get("agencies", [])
            ),  # agencies_with_prior_findings,
            audit_information.get("dollar_threshold"),
            Util.bool_to_yes_no(audit_information.get("is_low_risk_auditee", False)),
            Util.bool_to_yes_no(
                general_information.get("multiple_ueis_covered", False)
            ),  # "is_additional_ueis",
            Util.format_date(audit.created_at),  # date_created
            audit.fac_accepted_date,
            history_dict.get(
                EventType.LOCKED_FOR_CERTIFICATION
            ),  # ready_for_certification_date
            history_dict.get(EventType.SUBMITTED),  # submitted_date
            audit.data_source,
            audit.is_public,
        ]
    ]


general_information_excel = ExcelSheet(
    sheet_name="general",
    column_names=[
        "report_id",
        "audit_year",
        "total_amount_expended",
        "entity_type",
        "fy_start_date",
        "fy_end_date",
        "audit_type",
        "audit_period_covered",
        "number_months",
        "auditee_uei",
        "auditee_ein",
        "auditee_name",
        "auditee_address_line_1",
        "auditee_city",
        "auditee_state",
        "auditee_zip",
        "auditee_contact_name",
        "auditee_contact_title",
        "auditee_phone",
        "auditee_email",
        "auditee_certified_date",
        "auditee_certify_name",
        "auditee_certify_title",
        "auditor_ein",
        "auditor_firm_name",
        "auditor_address_line_1",
        "auditor_city",
        "auditor_state",
        "auditor_zip",
        "auditor_country",
        "auditor_contact_name",
        "auditor_contact_title",
        "auditor_phone",
        "auditor_email",
        "auditor_foreign_address",
        "auditor_certified_date",
        "auditor_certify_name",
        "auditor_certify_title",
        "cognizant_agency",
        "oversight_agency",
        "type_audit_code",
        "sp_framework_basis",
        "is_sp_framework_required",
        "is_going_concern_included",
        "is_internal_control_deficiency_disclosed",
        "is_internal_control_material_weakness_disclosed",
        "is_material_noncompliance_disclosed",
        "gaap_results",
        "is_aicpa_audit_guide_included",
        "sp_framework_opinions",
        "agencies_with_prior_findings",
        "dollar_threshold",
        "is_low_risk_auditee",
        "is_additional_ueis",
        "date_created",
        "fac_accepted_date",
        "ready_for_certification_date",
        "submitted_date",
        "data_source",
        "is_public",
    ],
    parse_audit_to_entries=_get_entry,
)
