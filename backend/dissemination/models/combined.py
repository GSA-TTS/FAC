from django.db import models
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class DisseminationCombined(models.Model):
    """
    Represents the 'dissemination_combined' materialized view.
    """

    # Meta options
    class Meta:
        managed = False
        db_table = "dissemination_combined"

    # General Information
    report_id = models.TextField(
        "Report ID",
        help_text=REPORT_ID_FK_HELP_TEXT,
        unique=True,
    )
    auditee_certify_name = models.TextField(
        "Name of Auditee Certifying Official",
        help_text=docs.auditee_certify_name,
    )
    auditee_certify_title = models.TextField(
        "Title of Auditee Certifying Official",
        help_text=docs.auditee_certify_title,
    )
    auditor_certify_name = models.TextField(
        "Name of Auditor Certifying Official",
        help_text=docs.auditor_certify_name,
    )
    auditor_certify_title = models.TextField(
        "Title of Auditor Certifying Official",
        help_text=docs.auditor_certify_title,
    )
    auditee_contact_name = models.TextField(
        "Name of Auditee Contact",
        help_text=docs.auditee_contact,
    )
    auditee_email = models.TextField(
        "Auditee Email address",
        help_text=docs.auditee_email,
    )
    auditee_name = models.TextField("Name of the Auditee", help_text=docs.auditee_name)
    auditee_phone = models.TextField(
        "Auditee Phone Number", help_text=docs.auditee_phone
    )
    auditee_contact_title = models.TextField(
        "Title of Auditee Contact",
        help_text=docs.auditee_title,
    )
    auditee_address_line_1 = models.TextField(
        "Auditee Street Address", help_text=docs.street1
    )
    auditee_city = models.TextField("Auditee City", help_text=docs.city)
    auditee_state = models.TextField("Auditee State", help_text=docs.state)
    auditee_ein = models.TextField(
        "Primary Employer Identification Number",
    )

    auditee_uei = models.TextField("Auditee UEI", help_text=docs.uei_general)

    is_additional_ueis = models.TextField()

    auditee_zip = models.TextField(
        "Auditee Zip Code",
        help_text=docs.zip_code,
    )
    auditor_phone = models.TextField("CPA phone number", help_text=docs.auditor_phone)

    auditor_state = models.TextField("CPA State", help_text=docs.auditor_state)
    auditor_city = models.TextField("CPA City", help_text=docs.auditor_city)
    auditor_contact_title = models.TextField(
        "Title of CPA Contact",
        help_text=docs.auditor_title,
    )
    auditor_address_line_1 = models.TextField(
        "CPA Street Address",
        help_text=docs.auditor_street1,
    )
    auditor_zip = models.TextField(
        "CPA Zip Code",
        help_text=docs.auditor_zip_code,
    )
    auditor_country = models.TextField("CPA Country", help_text=docs.auditor_country)
    auditor_contact_name = models.TextField(
        "Name of CPA Contact",
        help_text=docs.auditor_contact,
    )
    auditor_email = models.TextField(
        "CPA mail address (optional)",
        help_text=docs.auditor_email,
    )
    auditor_firm_name = models.TextField(
        "CPA Firm Name", help_text=docs.auditor_firm_name
    )
    # Once loaded, would like to add these as regular addresses and just change this to a country field
    auditor_foreign_address = models.TextField(
        "CPA Address - if international",
        help_text=docs.auditor_foreign,
    )
    auditor_ein = models.TextField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        help_text=docs.auditor_ein,
    )

    # Agency
    cognizant_agency = models.TextField(
        "Two digit Federal agency prefix of the cognizant agency",
        help_text=docs.cognizant_agency,
        null=True,
    )
    oversight_agency = models.TextField(
        "Two digit Federal agency prefix of the oversight agency",
        help_text=docs.oversight_agency,
        null=True,
    )

    # Dates
    date_created = models.DateField(
        "The first date an audit component or Form SF-SAC was received by the Federal audit Clearinghouse (FAC).",
        help_text=docs.initial_date_received,
    )
    ready_for_certification_date = models.DateField(
        "The date at which the audit transitioned to 'ready for certification'",
    )
    auditor_certified_date = models.DateField(
        "The date at which the audit transitioned to 'auditor certified'",
    )
    auditee_certified_date = models.DateField(
        "The date at which the audit transitioned to 'auditee certified'",
    )
    submitted_date = models.DateField(
        "The date at which the audit transitioned to 'submitted'",
    )
    fac_accepted_date = models.DateField(
        "The date at which the audit transitioned to 'accepted'",
    )

    fy_end_date = models.DateField("Fiscal Year End Date", help_text=docs.fy_end_date)
    fy_start_date = models.DateField(
        "Fiscal Year Start Date", help_text=docs.fy_start_date
    )
    audit_year = models.TextField(
        "Audit year from fy_start_date.",
        help_text=docs.audit_year_general,
    )

    audit_type = models.TextField(
        "Type of Audit",
        help_text=docs.audit_type,
    )

    # Audit Info
    gaap_results = models.TextField(
        "GAAP Results by Auditor",
    )  # Concatenation of choices
    sp_framework_basis = models.TextField(
        "Special Purpose Framework that was used as the basis of accounting",
        help_text=docs.sp_framework,
    )
    is_sp_framework_required = models.TextField(
        "Indicate whether or not the special purpose framework used as basis of accounting by state law or tribal law",
        help_text=docs.sp_framework_required,
    )
    sp_framework_opinions = models.TextField(
        "The auditor's opinion on the special purpose framework",
        help_text=docs.type_report_special_purpose_framework,
    )
    is_going_concern_included = models.TextField(
        "Whether or not the audit contained a going concern paragraph on financial statements",
        help_text=docs.going_concern,
    )
    is_internal_control_deficiency_disclosed = models.TextField(
        "Whether or not the audit disclosed a significant deficiency on financial statements",
        help_text=docs.significant_deficiency_general,
    )
    is_internal_control_material_weakness_disclosed = models.TextField(
        help_text=docs.material_weakness_general
    )
    is_material_noncompliance_disclosed = models.TextField(
        "Whether or not the audit disclosed a material noncompliance on financial statements",
        help_text=docs.material_noncompliance,
    )

    is_aicpa_audit_guide_included = models.TextField()
    dollar_threshold = models.BigIntegerField(
        "Dollar Threshold to distinguish between Type A and Type B programs.",
        help_text=docs.dollar_threshold,
    )
    is_low_risk_auditee = models.TextField(
        "Indicate whether or not the auditee qualified as a low-risk auditee",
        help_text=docs.low_risk,
    )
    agencies_with_prior_findings = models.TextField(
        "List of agencues with prior findings",
    )  # Concatenation of agency codes
    # End of Audit Info

    entity_type = models.TextField(
        "Self reported type of entity (i.e., States, Local Governments, Indian Tribes, Institutions of Higher Education, NonProfit)",
        help_text=docs.entity_type,
    )
    number_months = models.TextField(
        "Number of Months Covered by the 'Other' Audit Period",
        help_text=docs.number_months,
    )
    audit_period_covered = models.TextField(
        "Audit Period Covered by Audit", help_text=docs.period_covered
    )
    total_amount_expended = models.BigIntegerField(
        "Total Federal Expenditures",
        help_text=docs.total_fed_expenditures,
    )

    type_audit_code = models.TextField(
        "Determines if audit is A133 or UG",
    )

    is_public = models.BooleanField(
        "True for public records, False for non-public records", default=False
    )
    # Choices are: GSA, Census, or TESTDATA
    data_source = models.TextField("Data origin; GSA, Census, or TESTDATA")

    # Federal Award Details
    additional_award_identification = models.TextField(
        "Other data used to identify the award which is not a CFDA number (e.g., program year, contract number)",
        help_text=docs.award_identification,
    )
    amount_expended = models.BigIntegerField(
        "Amount Expended for the Federal Program",
        help_text=docs.amount,
    )
    award_reference = models.TextField(
        "Order that the award line was reported",
    )
    cluster_name = models.TextField(
        "The name of the cluster",
        help_text=docs.cluster_name,
    )
    cluster_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name",
        help_text=docs.cluster_total,
    )
    federal_agency_prefix = models.TextField(
        "2-char code refers to an agency",
    )
    federal_award_extension = models.TextField(
        "3-digit extn for a program defined by the agency",
    )
    aln = models.TextField(
        "2-char agency code concatenated to 3-digit program extn",
    )
    federal_program_name = models.TextField(
        "Name of Federal Program",
        help_text=docs.federal_program_name,
    )
    federal_program_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension",
        help_text=docs.program_total,
    )
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)",
        help_text=docs.findings_count,
    )
    is_direct = models.TextField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        help_text=docs.direct,
    )
    is_loan = models.TextField(
        "Indicate whether or not the program is a Loan or Loan Guarantee (only available for audit years 2013 and beyond)",
        help_text=docs.loans,
    )
    is_major = models.TextField(
        "Indicate whether or not the Federal program is a major program",
        help_text=docs.major_program,
    )
    is_passthrough_award = models.TextField(
        "Indicates whether or not funds were passed through to any subrecipients for the Federal program",
        help_text=docs.passthrough_award,
    )
    loan_balance = models.TextField(
        "The loan or loan guarantee (loan) balance outstanding at the end of the audit period.  A response of ‘N/A’ is acceptable.",
        help_text=docs.loan_balance,
    )
    audit_report_type = models.TextField(
        "Type of Report Issued on the Major Program Compliance",
        help_text=docs.type_report_major_program_cfdainfo,
    )
    other_cluster_name = models.TextField(
        "The name of the cluster (if not listed in the Compliance Supplement)",
        help_text=docs.other_cluster_name,
    )
    passthrough_amount = models.BigIntegerField(
        "Amount passed through to subrecipients",
        help_text=docs.passthrough_amount,
        null=True,
    )
    state_cluster_name = models.TextField(
        "The name of the state cluster",
        help_text=docs.state_cluster_name,
    )

    # Finding Details
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

    # each element in the list is a FK to Finding
    type_requirement = models.TextField(
        "Type Requirement Failure",
        help_text=docs.type_requirement_findings,
    )

    passthrough_id = models.TextField(
        "Identifying Number Assigned by the Pass-through Entity",
        help_text=docs.passthrough_id,
    )
    passthrough_name = models.TextField(
        "Name of Pass-through Entity",
        help_text=docs.passthrough_name,
    )
