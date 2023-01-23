# importing django models and users
from django.db import models
from django.contrib.auth.models import User

# Models that mimic the downloads
class General(models.Model):
    audit_type = models.CharField("Type of Audit", max_length=40)
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    auditee_certify_name = models.CharField(
        "Name of Auditee Certifying Official", max_length=50, null=True
    )
    auditee_certify_title = models.CharField(
        "Title of Auditee Certifying Official", max_length=50, null=True
    )
    auditee_contact = models.CharField("Name of Auditee Contact", max_length=50)
    auditee_date_signed = models.DateField("Date of auditee signature")
    auditee_email = models.CharField(
        "Auditee Email address",
        max_length=60,
        null=True,
    )
    auditee_fax = models.PositiveBigIntegerField(
        "Auditee Fax Number (optional)",
        null=True,
    )  # , max_length=10)
    auditee_name = models.CharField("Name of the Auditee", max_length=70)
    auditee_name_title = models.CharField(
        "Title of Auditee Certifying Official", max_length=70
    )
    auditee_phone = models.PositiveBigIntegerField(
        "Auditee Phone Number"
    )  # , max_length=10)
    auditee_title = models.CharField("Title of Auditee Contact", max_length=40)
    auditor_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)"
    )  # , max_length=9)
    city = models.CharField("Auditee City", max_length=30)
    # not actually digits in data
    cognizant_agency = models.CharField(
        "Two digit Federal agency prefix of the cognizant agency",
        max_length=2,
        null=True,
    )
    cognizant_agency_over = models.CharField(max_length=2, null=True)
    completed_on = models.DateField(
        "Date the Audit was Posted to the Internet as Complete", null=True
    )
    component_date_received = models.DateField(
        "The most recent date an audit component was received by the FAC. This field was not populated before 2004. Receipt of Financial statements only are not processed until the rest of the audit or a Form SF-SAC is also received.",
        null=True,
    )
    condition_or_deficiency = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition/significant deficiency on financial statements",
        null=True,
    )
    condition_or_deficiency_major_program = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition/significant deficiency for any major program in the Schedule of Findings and Questioned Costs",
        null=True,
    )
    cpa_city = models.CharField("CPA City", max_length=30)
    cpa_contact = models.CharField("Name of CPA Contact", max_length=50)
    cpa_country = models.CharField("CPA Country", max_length=6, null=True)
    cpa_date_signed = models.DateField("Date of CPA signature")
    cpa_email = models.CharField("CPA email address", max_length=60, null=True)
    cpa_fax = models.PositiveBigIntegerField(
        "CPA fax number (optional)", null=True
    )  # , max_length=10)
    cpa_firm_name = models.CharField("CPA Firm Name", max_length=64)
    cpa_foreign = models.CharField(
        "CPA Address - if international", max_length=200, null=True
    )
    cpa_phone = models.PositiveBigIntegerField("CPA phone number")  # , max_length=10)
    cpa_state = models.CharField("CPA State", max_length=2)
    cpa_street1 = models.CharField("CPA Street Address", max_length=45)
    cpa_street2 = models.CharField("CPA Street Address", max_length=45, null=True)
    cpa_title = models.CharField("Title of CPA Contact", max_length=40)
    cpa_zip_code = models.IntegerField("CPA Zip Code")  # , max_length=9)
    current_or_former_findings = models.BooleanField(
        "Indicate whether or not current year findings or prior year findings affecting direct funds were reported",
        null=True,
    )
    date_firewall = models.DateField(null=True)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    dollar_threshold = models.FloatField(
        "Dollar Threshold to distinguish between Type A and Type B programs.", null=True
    )
    duns = models.IntegerField(
        "Primary Data Universal Numbering System Number", null=True
    )  # , max_length=9)
    dup_reports = models.BooleanField(
        "Whether or not the financial statements include departments that have separate expenditures not included in this audit",
        null=True,
    )
    ein = models.IntegerField(
        "Primary Employer Identification Number"
    )  # , max_length=9)
    ein_subcode = models.IntegerField(
        "Subcode assigned to the EIN", null=True
    )  # , max_length=3)
    entity_type = models.CharField(
        "Self reported type of entity (i.e., States, Local Governments, Indian Tribes, Institutions of Higher Education, NonProfit)",
        max_length=50,
    )
    fac_accepted_date = models.DateField(
        "The most recent date an audit report was submitted to the FAC that passed FAC screening and was accepted as a valid OMB Circular A-133 report submission."
    )
    form_date_received = models.DateField(
        "The most Recent Date the Form SF-SAC was received by the FAC. This field was not populated before 2001.",
        null=True,
    )
    fy_end_date = models.DateField("Fiscal Year End Date")
    fy_start_date = models.DateField("Fiscal Year Start Date", null=True)
    going_concern = models.BooleanField(
        "Whether or not the audit contained a going concern paragraph  on financial statements",
        null=True,
    )
    initial_date_received = models.DateField(
        "The first date an audit component or Form SF-SAC was received by the Federal audit Clearinghouse (FAC).",
        null=True,
    )
    low_risk = models.BooleanField(
        "Indicate whether or not the auditee qualified as a low-risk auditee", null=True
    )
    material_noncompliance = models.BooleanField(
        "Whether or not the audit disclosed a material noncompliance on financial statements",
        null=True,
    )
    material_weakness = models.BooleanField(
        "Whether or not the audit disclosed any reportable condition/significant deficiency as a material weakness on financial statements",
        null=True,
    )
    material_weakness_major_program = models.BooleanField(
        "Indicate whether any reportable condition/signficant deficiency was disclosed as a material weakness for a major program in the Schedule of Findings and Questioned Costs",
        null=True,
    )
    multiple_cpas = models.BooleanField(
        "Identifies if the Submission Contains Multiple CPAs", null=True
    )
    multiple_duns = models.BooleanField(
        "Identifies if the Submission Contains Multiple DUNS", null=True
    )
    multiple_eins = models.BooleanField(
        "Identifies if the Submission Contains Multiple EINs", null=True
    )
    multiple_ueis = models.BooleanField(
        "Identifies if the Submission Contains Multiple UEIs", null=True
    )
    number_months = models.IntegerField(
        "Number of Months Covered by the 'Other' Audit Period", null=True
    )
    oversight_agency = models.IntegerField(
        "Two digit Federal agency prefix of the oversight agency", null=True
    )  # , max_length=2)
    period_covered = models.CharField("Audit Period Covered by Audit", max_length=40)
    previous_completed_on = models.DateField(
        "Date the Audit was Previously Posted to the Internet as Complete", null=True
    )
    previous_date_firewall = models.DateField(null=True)
    prior_year_schedule = models.BooleanField(
        "Indicate whether or not the report includes a Summary Schedule of Prior Year Audit Findings",
        null=True,
    )
    questioned_costs = models.BooleanField(
        "Indicate whether or not the audit disclosed any known questioned costs.",
        null=True,
    )
    report_required = models.BooleanField(
        "Distribution to Federal Agency required?", null=True
    )
    sp_framework = models.CharField(
        "Special Purpose Framework that was used as the basis of accounting",
        max_length=40,
        null=True,
    )
    sp_framework_required = models.BooleanField(
        "Indicate whether or not the special purpose framework used as basis of accounting by state law or tribal law",
        null=True,
    )
    state = models.CharField("Auditee State", max_length=2)
    street1 = models.CharField("Auditee Street Address", max_length=45)
    street2 = models.CharField("Auditee Street Address", max_length=45, null=True)
    total_fed_expenditures = models.BigIntegerField(
        "Total Federal Expenditures"
    )  # , max_length=12)
    type_of_entity = models.CharField("Contact FAC for information", max_length=40)
    type_report_financial_statements = models.CharField(
        "Type of Report Issued on the Financial Statements", max_length=40, null=True
    )
    type_report_major_program = models.CharField(
        "Type of Report Issued on the Major Program Compliance",
        max_length=40,
        null=True,
    )
    type_report_special_purpose_framework = models.CharField(
        "The auditor's opinion on the special purpose framework",
        max_length=40,
        null=True,
    )
    uei = models.CharField("Unique Entity ID", max_length=12)
    zip_code = models.IntegerField("Auditee Zipcode")  # , max_length=9)
    # Not in key
    # DATEFIREWALL
    # PREVIOUSDATEFIREWALL


class CfdaInfo(models.Model):
    research_and_development = models.BooleanField(
        "Indicate whether or not the program is a Research and Development program",
        null=True,
    )
    loans = models.BooleanField(
        "Indicate whether or not the program is a Loan or Loan Guarantee (only available for audit years 2013 and beyond)",
        null=True,
    )
    arra = models.BooleanField(
        "American Recovery and Reinvestment Act Funded Program", null=True
    )
    direct = models.BooleanField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        null=True,
    )
    passthrough_award = models.BooleanField(
        "Indicates whether or not funds were passed through to any subrecipients for the Federal program",
        null=True,
    )
    major_program = models.BooleanField(
        "Indicate whether or not the Federal program is a major program", null=True
    )
    finding_ref_nums = models.CharField(
        "Findings Reference Numbers", max_length=100, null=True
    )
    amount = models.BigIntegerField(
        "Amount Expended for the Federal Program"
    )  # , max_length=12)
    program_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension"
    )  # , max_length=12)
    cluster_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name"
    )  # , max_length=12)
    passthrough_amount = models.BigIntegerField(
        "Amount passed through to subrecipients", null=True
    )  # , max_length=12)
    loan_balance = models.CharField(
        "The loan or loan guarantee (loan) balance outstanding at the end of the audit period.  A response of ‘N/A’ is acceptable.",
        max_length=40,
        null=True,
    )
    federal_program_name = models.CharField("Name of Federal Program", max_length=300)
    cfda_program_name = models.CharField(
        "Name of Federal Program (auto-generated by FAC from the CFDA catalog)",
        max_length=300,
    )
    award_identification = models.CharField(
        "Other data used to identify the award which is not a CFDA number (e.g., program year, contract number)",
        max_length=50,
    )
    # can have letters
    cfda = models.CharField("Federal Agency Prefix and Extension", max_length=52)
    cluster_name = models.CharField("The name of the cluster", max_length=75, null=True)
    state_cluster_name = models.CharField(
        "The name of the state cluster", max_length=75, null=True
    )
    other_cluster_name = models.CharField(
        "The name of the cluster (if not listed in the Compliance Supplement)",
        max_length=75,
        null=True,
    )
    type_requirement = models.CharField(
        "Type Requirement Failure", max_length=40, null=True
    )
    type_report_major_program = models.CharField(
        "Type of Report Issued on the Major Program Compliance", max_length=40
    )
    # not in key for this table check descriptions
    findings = models.TextField("Items on the Findings page", null=True)
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)"
    )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings"
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    ein = models.IntegerField(
        "Primary Employer Identification Number"
    )  # , max_length=9)
    # check this- it is QCOSTS2
    questioned_costs = models.CharField(
        "Questioned Costs",
        null=True,
        max_length=40,
    )


class Findings(models.Model):
    modified_opinion = models.BooleanField("Modified Opinion finding", null=True)
    other_non_compliance = models.BooleanField("Other Noncompliance finding", null=True)
    material_weakness = models.BooleanField("Material Weakness finding", null=True)
    significant_deficiency = models.BooleanField(
        "Significant Deficiency finding", null=True
    )
    other_findings = models.BooleanField("Other findings", null=True)
    questioned_costs = models.BooleanField("Questioned Costs", null=True)
    repeat_finding = models.BooleanField(
        "Indicates whether or not the audit finding was a repeat of an audit finding in the immediate prior audit",
        null=True,
    )
    finding_ref_nums = models.CharField("Findings Reference Numbers", max_length=100)
    prior_finding_ref_nums = models.CharField(
        "Audit finding reference numbers from the immediate prior audit", max_length=100
    )
    type_requirement = models.CharField("Type Requirement Failure", max_length=40)
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings"
    )
    elec_audit_findings_id = models.IntegerField(
        "FAC system generated sequence number for finding"
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class Findingstext(models.Model):
    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
    )
    finding_ref_nums = models.CharField(
        "Audit Finding Reference Number", max_length=100
    )
    seq_number = models.IntegerField(
        "Order that the findings text was reported"
    )  # , max_length=4)
    text = models.TextField("Content of the finding text")
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class Captext(models.Model):
    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
    )
    finding_ref_nums = models.CharField(
        "Audit Finding Reference Number", max_length=100
    )
    seq_number = models.IntegerField(
        "Order that the CAP text was reported"
    )  # , max_length=4)
    text = models.TextField("Content of the Corrective Action Plan (CAP)")
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class Notes(models.Model):
    type_id = models.CharField("Note Type", max_length=1)
    fac_id = models.IntegerField(
        "Internal Unique Identifier for the record"
    )  # , max_length=12)
    report_id = models.IntegerField("Internal Audit Report Id")  # , max_length=12)
    version = models.IntegerField("Internal Version")  # , max_length=4)
    seq_number = models.IntegerField(
        "Order that the Note was reported"
    )  # , max_length=4)
    note_index = models.IntegerField("Display Index for the Note")  # , max_length=4)
    content = models.TextField("Content of the Note")
    title = models.CharField("Note Title", max_length=75)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class MultipleCpasInfo(models.Model):
    cpa_phone = models.PositiveBigIntegerField(
        "CPA phone number",
        null=True,
    )  # , max_length=10)
    cpa_fax = models.PositiveBigIntegerField(
        "CPA fax number (optional)",
        null=True,
    )  # , max_length=10)
    cpa_state = models.CharField("CPA State", max_length=2)
    cpa_city = models.CharField("CPA City", max_length=30)
    cpa_title = models.CharField("Title of CPA Contact", max_length=40)
    cpa_street1 = models.CharField("CPA Street Address", max_length=45)
    cpa_zip_code = models.IntegerField(
        "CPA Zip Code",
        null=True,
    )  # , max_length=9)
    cpa_contact = models.CharField("Name of CPA Contact", max_length=50)
    cpa_email = models.CharField(
        "CPA mail address (optional)",
        max_length=60,
        null=True,
    )
    cpa_firm_name = models.CharField("CPA Firm Name", max_length=64)
    cpa_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        null=True,
    )  # , max_length=9)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    seqnum = models.IntegerField(
        "Order that Auditors were reported on page 5 of SF-SAC", null=True
    )


class Revisions(models.Model):
    findings = models.CharField(
        "Indicates what items on the Findings page were edited during the revision",
        max_length=110,
    )
    elec_report_revision_id = models.IntegerField(
        "Internal Unique Identifier for the record"
    )  # , max_length=12)
    federal_awards = models.CharField(
        "Indicates what items on the Federal Awards page were edited during the revision",
        max_length=140,
    )
    general_info_explain = models.CharField(
        "Explanation of what items on the General Info page were edited during the revision",
        max_length=150,
    )
    federal_awards_explain = models.TextField(
        "Explanation of what items on the Federal Awards page were edited during the revision",
    )
    notes_to_sefa_explain = models.TextField(
        "Explanation of what items on the Notes to SEFA page were edited during the revision",
    )
    auditinfo_explain = models.TextField(
        "Explanation of what items on the Audit Info page were edited during the revision",
    )
    findings_explain = models.TextField(
        "Explanation of what items on the Findings page were edited during the revision",
    )
    findings_text_explain = models.TextField(
        "Explanation of what items on the Text of the Audit Findings page were edited during the revision",
    )
    cap_explain = models.TextField(
        "Explanation of what items on the CAP Text page were edited during the revision",
    )
    other_explain = models.TextField(
        "Explanation of what other miscellaneous items were edited during the revision",
    )
    audit_info = models.CharField(
        "Indicates what items on the Audit Info page were edited during the revision",
        max_length=200,
    )
    notes_to_sefa = models.CharField(
        "Indicates what items on the Notes to SEFA page were edited during the revision",
        max_length=50,
    )
    findings_text = models.CharField(
        "Indicates what items on the Text of the Audit Findings page were edited during the revision",
        max_length=6,
    )
    cap = models.CharField(
        "Indicates what items on the CAP Text page were edited during the revision",
        max_length=6,
    )
    other = models.CharField(
        "Indicates what other miscellaneous items were edited during the revision",
        max_length=65,
    )
    general_info = models.CharField(
        "Indicates what items on the General Info page were edited during the revision",
        max_length=75,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class UeiInfo(models.Model):
    uei = models.CharField("Multiple Unique Entity Identifier Numbers", max_length=12)
    uei_seq_num = models.IntegerField(
        "Order that UEI was reported on page 4 of SF-SAC"
    )  # , max_length=40)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class Agencies(models.Model):
    agency_cfda = models.IntegerField(
        "2-digit prefix of Federal Agency requiring copy of audit report"
    )  # , max_length=2)
    ein = models.IntegerField(
        "Employer Identification Number (EIN) of primary grantee", null=True
    )  # , max_length=9)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class Passthrough(models.Model):
    passthrough_name = models.CharField("Name of Pass-through Entity", max_length=70)
    passthrough_id = models.CharField(
        "Identifying Number Assigned by the Pass-through Entity", max_length=70
    )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Passthrough data between CFDA Info and Passthrough"
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key",
        max_length=40,
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key",
        max_length=40,
    )


class EinInfo(models.Model):
    ein = models.IntegerField(
        "Multiple Employer Identification Numbers"
    )  # , max_length=9)
    ein_seq_num = models.IntegerField(
        "Order that EINs were reported on page 4 of SF-SAC"
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )


class DunsInfo(models.Model):
    duns = models.IntegerField(
        "Multiple Data Universal Numbering System Numbers"
    )  # , max_length=9)
    duns_seq_num = models.IntegerField(
        "Order that DUNS was reported on page 4 of SF-SAC"
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
    )
