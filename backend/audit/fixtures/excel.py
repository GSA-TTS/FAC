FEDERAL_AWARDS_TEMPLATE = "excel_templates/federal-awards-expended-template.xlsx"
FINDINGS_TEXT_TEMPLATE = "excel_templates/findings-text-template.xlsx"

FEDERAL_AWARDS_TEMPLATE_DEFINITION = "federal-awards-expended-template.json"
CORRECTIVE_ACTION_TEMPLATE_DEFINITION = "corrective-action-plan-template.json"
FINDINGS_UNIFORM_TEMPLATE_DEFINITION = "findings-uniform-guidance-template.json"
FINDINGS_TEXT_TEMPLATE_DEFINITION = "findings-text-template.json"

CORRECTIVE_ACTION_PLAN_TEMPLATE = "excel_templates/corrective-action-plan-template.xlsx"
FINDINGS_UNIFORM_GUIDANCE_TEMPLATE = (
    "excel_templates/findings-uniform-guidance-template.xlsx"
)
CORRECTIVE_ACTION_PLAN_TEST_FILE = "test-files/corrective-action-plan-pass-01.json"
FINDINGS_TEXT_TEST_FILE = "test-files/findings-text-pass-01.json"
FINDINGS_UNIFORM_GUIDANCE_TEST_FILE = (
    "test-files/findings-uniform-guidance-pass-01.json"
)

CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES = [
    {
        "contains_chart_or_table": "Y",
        "planned_action": "corrective action 1",
        "reference_number": "2023-001",
    },
    {
        "contains_chart_or_table": "N",
        "planned_action": "corrective action 2",
        "reference_number": "2023-002",
    },
]

FINDINGS_TEXT_ENTRY_FIXTURES = [
    {
        "contains_chart_or_table": "N",
        "text_of_finding": "This is an audit finding",
        "reference_number": "2023-001",
    },
    {
        "contains_chart_or_table": "Y",
        "text_of_finding": "Here is another audit finding",
        "reference_number": "2023-002",
    },
]

FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES = [
    {
        "federal_agency_prefix": "10",
        "three_digit_extension": "001",
        "program_name": "program name",
        "compliance_requirement": "AB",
        "reference_number": "2023-001",
        "repeat_prior_reference": "Y",
        "prior_references": "2020-001",
        "is_valid": "Y",
        "questioned_costs": "N",
        "significant_deficiency": "N",
        "other_matters": "N",
        "other_findings": "N",
        "modified_opinion": "Y",
        "material_weakness": "N",
    },
    {
        "federal_agency_prefix": "10",
        "three_digit_extension": "002",
        "program_name": "program name",
        "compliance_requirement": "E",
        "reference_number": "2023-001",
        "repeat_prior_reference": "N",
        "is_valid": "Y",
        "questioned_costs": "N",
        "significant_deficiency": "N",
        "other_matters": "Y",
        "other_findings": "N",
        "modified_opinion": "N",
        "material_weakness": "Y",
    },
]

FEDERAL_AWARDS_ENTRY_FIXTURES = [
    {
        "federal_agency_prefix": "10",
        "three_digit_extension": "001",
        "amount_expended": 100,
        "cluster_name": "N/A",
        "is_direct": "N",
        "passthrough_name": "A|B",
        "passthrough_identifying_number": "1|2",
        "is_passed": "N",
        "subrecipient_amount": 0,
        "program_name": "program name",
        "loan_balance_at_audit_period_end": 0,
        "is_guaranteed": "N",
        "is_major": "Y",
        "audit_report_type": "U",
        "number_of_audit_findings": 0,
        "state_cluster_name": "",
        "cluster_total": 123,
    },
    {
        "federal_agency_prefix": "10",
        "three_digit_extension": "U12",
        "additional_award_identification": "1234",
        "amount_expended": 100,
        "cluster_name": "N/A",
        "is_direct": "N",
        "passthrough_name": "C|D",
        "passthrough_identifying_number": "3|4",
        "is_passed": "N",
        "subrecipient_amount": 0,
        "program_name": "program name",
        "loan_balance_at_audit_period_end": 0,
        "is_guaranteed": "N",
        "is_major": "Y",
        "audit_report_type": "U",
        "number_of_audit_findings": 0,
        "state_cluster_name": "",
        "cluster_total": 123,
    },
]

FEDERAL_AWARDS_EXPENDED = "FederalAwardsExpended"
CORRECTIVE_ACTION_PLAN = "CorrectiveActionPlan"
FINDINGS_TEXT = "FindingsText"
FINDINGS_UNIFORM_GUIDANCE = "FindingsUniformGuidance"
