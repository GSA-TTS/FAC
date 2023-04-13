FEDERAL_AWARDS_TEMPLATE = "excel_templates/FederalAwardsExpendedTemplateUG2019.xlsx"
CORRECTIVE_ACTION_PLAN_TEMPLATE = "excel_templates/CorrectiveActionPlanTemplate2019-2022.xlsx"

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
