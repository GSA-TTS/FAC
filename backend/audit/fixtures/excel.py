FEDERAL_AWARDS_TEMPLATE = "excel_templates/FederalAwardsExpendedTemplateUG2019.xlsx"
CORRECTIVE_ACTION_PLAN_TEMPLATE = "excel_templates/CorrectiveActionPlanTemplate2019-2022.xlsx"
FINDINGS_UNIFORM_GUIDANCE_TEMPLATE = "excel_templates/FindingsUniformGuidanceTemplate2019-2022.xlsx"
CORRECTIVE_ACTION_PLAN_TEST_FILE = "test-files/corrective-action-plan-pass-01.json"
FINDINGS_UNIFORM_GUIDANCE_TEST_FILE = "test-files/findings-uniform-guidance-pass-01.json"

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

FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES = [
    {
        "program_name": "program name",
        "compliance_requirement": "AB",
        "finding_reference_number": "2023-001",
        "repeat_prior_reference": "Y",
        "prior_references": "2020-001",
        "is_valid": "Y",
        "questioned_costs": "N",
        "significiant_deficiency": "N",
        "other_matters": "N",
        "other_findings": "N",
        "modified_opinion": "Y",
        "material_weakness": "N",
        "program_number": "10.001",
    },
    {
        "program_name": "program name",
        "compliance_requirement": "E",
        "finding_reference_number": "2023-001",
        "repeat_prior_reference": "N",
        "is_valid": "Y",
        "questioned_costs": "N",
        "significiant_deficiency": "N",
        "other_matters": "Y",
        "other_findings": "N",
        "modified_opinion": "N",
        "material_weakness": "Y",
        "program_number": "10.002",
    }
]

FEDERAL_AWARDS_ENTRY_FIXTURES = [
    {
        "amount_expended": 100,
        "cluster_name": "N/A",
        "direct_award": "N",
        "direct_award_pass_through_entity_name": "A|B",
        "direct_award_pass_through_entity_id": "1|2",
        "federal_award_passed_to_subrecipients": "N",
        "federal_award_passed_to_subrecipients_amount": 0,
        "federal_program_name": "program name",
        "loan_balance_at_audit_period_end": 0,
        "loan_or_loan_guarantee": "N",
        "major_program": "Y",
        "major_program_audit_report_type": "U",
        "number_of_audit_findings": 0,
        "program_number": "10.001",
        "state_cluster_name": "",
    },
    {
        "amount_expended": 100,
        "cluster_name": "N/A",
        "direct_award": "N",
        "direct_award_pass_through_entity_name": "C|D",
        "direct_award_pass_through_entity_id": "3|4",
        "federal_award_passed_to_subrecipients": "N",
        "federal_award_passed_to_subrecipients_amount": 0,
        "federal_program_name": "program name",
        "loan_balance_at_audit_period_end": 0,
        "loan_or_loan_guarantee": "N",
        "major_program": "Y",
        "major_program_audit_report_type": "U",
        "number_of_audit_findings": 0,
        "program_number": "10.002",
        "state_cluster_name": "",
    },
]

FEDERAL_AWARDS_EXPENDED = "FederalAwardsExpended"
CORRECTIVE_ACTION_PLAN = "CorrectiveActionPlan"
FINDINGS_TEXT = "FindingsText"
FINDINGS_UNIFORM_GUIDANCE = "FindingsUniformGuidance"
