# importing django models and users
from django.db import models
from django.contrib.auth.models import User

# Models that mimic the downloads
class General(models.Model):
    audit_type = models.CharField("Type of Audit", max_length=40, description=docs.audit_type )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_general )
    auditee_certify_name = models.CharField(
        "Name of Auditee Certifying Official", max_length=50, null=True,
     description=docs.auditee_certify_name )
    auditee_certify_title = models.CharField(
        "Title of Auditee Certifying Official", max_length=50, null=True,
     description=docs.auditee_certify_title )
    auditee_contact = models.CharField("Name of Auditee Contact", max_length=50, description=docs.auditee_contact )
    auditee_date_signed = models.DateField("Date of Auditee signature" description=docs.auditee_date_signed )
    auditee_email = models.CharField(
        "Auditee Email address",
        max_length=60,
        null=True,
     description=docs.auditee_email )
    auditee_fax = models.PositiveBigIntegerField(
        "Auditee Fax Number (optional)",
        null=True,
     description=docs.auditee_fax )  # , max_length=10
    auditee_name = models.CharField("Name of the Auditee", max_length=70, description=docs.auditee_name )
    auditee_name_title = models.CharField(
        "Title of Auditee Certifying Official", max_length=70,
     description=docs.auditee_name_title )
    auditee_phone = models.PositiveBigIntegerField(
        "Auditee Phone Number"
     description=docs.auditee_phone )  # , max_length=10
    auditee_title = models.CharField("Title of Auditee Contact", max_length=40, description=docs.auditee_title )
    auditor_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)"
     description=docs.auditor_ein )  # , max_length=9
    city = models.CharField("Auditee City", max_length=30, description=docs.city )
    # not actually digits in data
    cognizant_agency = models.CharField(
        "Two digit Federal agency prefix of the cognizant agency",
        max_length=2,
        null=True,
     description=docs.cognizant_agency )
    ## needs documentation ##
    cognizant_agency_over = models.CharField(max_length=2, null=True)
    completed_on = models.DateField(
        "Date the Audit was Posted to the Internet as Complete", null=True
     description=docs.completed_on )
    component_date_received = models.DateField(
        "The most recent date an audit component was received by the FAC. This field was not populated before 2004. Receipt of Financial statements only are not processed until the rest of the audit or a Form SF-SAC is also received.",
        null=True,
     description=docs.component_date_received )
    condition_or_deficiency = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition/significant deficiency on financial statements",
        null=True,
     description=docs.condition_or_deficiency )
    condition_or_deficiency_major_program = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition/significant deficiency for any major program in the Schedule of Findings and Questioned Costs",
        null=True,
     description=docs.condition_or_deficiency_major_program )
    cpa_city = models.CharField("CPA City", max_length=30, description=docs.cpa_city_general )
    cpa_contact = models.CharField("Name of CPA Contact", max_length=50, description=docs.cpa_contact_general )
    cpa_country = models.CharField("CPA Country", max_length=6, null=True,description=docs.cpa_country )
    cpa_date_signed = models.DateField("Date of CPA signature" description=docs.cpa_date_signed )
    cpa_email = models.CharField("CPA email address", max_length=60, null=True, description=docs.cpa_email_general )
    cpa_fax = models.PositiveBigIntegerField(
        "CPA fax number (optional ", null=True,
     description=docs.cpa_fax_general )  # , max_length=10
    cpa_firm_name = models.CharField("CPA Firm Name", max_length=64, description=docs.cpa_firm_name_general )
    cpa_foreign = models.CharField(
        "CPA Address - if international", max_length=200, null=True,
     description=docs.cpa_foreign )
    cpa_phone = models.PositiveBigIntegerField("CPA phone number" description=docs.cpa_phone_general )  # , max_length=10
    cpa_state = models.CharField("CPA State", max_length=2, description=docs.cpa_state_general )
    cpa_street1 = models.CharField("CPA Street Address", max_length=45, description=docs.cpa_street1_general )
    cpa_street2 = models.CharField("CPA Street Address", max_length=45, null=True, description=docs.cpa_street2 )
    cpa_title = models.CharField("Title of CPA Contact", max_length=40, description=docs.cpa_title_general )
    cpa_zip_code = models.IntegerField("CPA Zip Code" description=docs.cpa_zip_code_general )  # , max_length=9
    current_or_former_findings = models.BooleanField(
        "Indicate whether or not current year findings or prior year findings affecting direct funds were reported",
        null=True,
     description=docs.current_or_former_findings )
    ## needs documentation ##
    date_firewall = models.DateField(null=True)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_general )
    dollar_threshold = models.FloatField(
        "Dollar Threshold to distinguish between Type A and Type B programs.", null=True,
     description=docs.dollar_threshold )
    duns = models.IntegerField(
        "Primary Data Universal Numbering System Number", null=True,
     description=docs.duns_general )  # , max_length=9
    dup_reports = models.BooleanField(
        "Whether or not the financial statements include departments that have separate expenditures not included in this audit",
        null=True,
     description=docs.dup_reports )
    ein = models.IntegerField(
        "Primary Employer Identification Number"
     description=docs.ein_general )  # , max_length=9
    ein_subcode = models.IntegerField(
        "Subcode assigned to the EIN", null=True
     description=docs.ein_subcode )  # , max_length=3
    entity_type = models.CharField(
        "Self reported type of entity (i.e., States, Local Governments, Indian Tribes, Institutions of Higher Education, NonProfit)",
        max_length=50,
     description=docs.entity_type )
    fac_accepted_date = models.DateField(
        "The most recent date an audit report was submitted to the FAC that passed FAC screening and was accepted as a valid OMB Circular A-133 report submission."
     description=docs.fac_accepted_date )
    form_date_received = models.DateField(
        "The most Recent Date the Form SF-SAC was received by the FAC. This field was not populated before 2001.",
        null=True,
     description=docs.form_date_received )
    fy_end_date = models.DateField("Fiscal Year End Date" description=docs.fy_end_date )
    fy_start_date = models.DateField("Fiscal Year Start Date", null=True description=docs.fy_start_date )
    going_concern = models.BooleanField(
        "Whether or not the audit contained a going concern paragraph  on financial statements",
        null=True,
     description=docs.going_concern )
    initial_date_received = models.DateField(
        "The first date an audit component or Form SF-SAC was received by the Federal audit Clearinghouse (FAC).",
        null=True,
     description=docs.initial_date_received )
    low_risk = models.BooleanField(
        "Indicate whether or not the auditee qualified as a low-risk auditee", null=True,
     description=docs.low_risk )
    material_noncompliance = models.BooleanField(
        "Whether or not the audit disclosed a material noncompliance on financial statements",
        null=True,
     description=docs.material_noncompliance )
    material_weakness = models.BooleanField(
        "Whether or not the audit disclosed any reportable condition/significant deficiency as a material weakness on financial statements",
        null=True,
     description=docs.material_weakness_general )
    material_weakness_major_program = models.BooleanField(
        "Indicate whether any reportable condition/signficant deficiency was disclosed as a material weakness for a major program in the Schedule of Findings and Questioned Costs",
        null=True,
     description=docs.material_weakness_major_program )
    multiple_cpas = models.BooleanField(
        "Identifies if the Submission Contains Multiple CPAs", null=True,
     description=docs.multiple_cpas )
    multiple_duns = models.BooleanField(
        "Identifies if the Submission Contains Multiple DUNS", null=True,
     description=docs.multiple_duns )
    multiple_eins = models.BooleanField(
        "Identifies if the Submission Contains Multiple EINs", null=True,
     description=docs.multiple_eins )
    multiple_ueis = models.BooleanField(
        "Identifies if the Submission Contains Multiple UEIs", null=True,
     description=docs.multiple_ueis )
    number_months = models.IntegerField(
        "Number of Months Covered by the 'Other' Audit Period", null=True,
     description=docs.number_months )
    oversight_agency = models.IntegerField(
        "Two digit Federal agency prefix of the oversight agency", null=True,
     description=docs.oversight_agency )  # , max_length=2
    period_covered = models.CharField("Audit Period Covered by Audit", max_length=40, description=docs.period_covered )
    previous_completed_on = models.DateField(
        "Date the Audit was Previously Posted to the Internet as Complete", null=True,
     description=docs.previous_completed_on )
    ### needs documentation ###
    previous_date_firewall = models.DateField(null=True)
    prior_year_schedule = models.BooleanField(
        "Indicate whether or not the report includes a Summary Schedule of Prior Year Audit Findings",
        null=True,
     description=docs.prior_year_schedule )
    questioned_costs = models.BooleanField(
        "Indicate whether or not the audit disclosed any known questioned costs.",
        null=True,
     description=docs.questioned_costs_general )
    report_required = models.BooleanField(
        "Distribution to Federal Agency required?", null=True,
     description=docs.report_required )
    sp_framework = models.CharField(
        "Special Purpose Framework that was used as the basis of accounting",
        max_length=40,
        null=True,
     description=docs.sp_framework )
    sp_framework_required = models.BooleanField(
        "Indicate whether or not the special purpose framework used as basis of accounting by state law or tribal law",
        null=True,
     description=docs.sp_framework_required )
    state = models.CharField("Auditee State", max_length=2, description=docs.state )
    street1 = models.CharField("Auditee Street Address", max_length=45, description=docs.street1 )
    street2 = models.CharField("Auditee Street Address", max_length=45, null=True, description=docs.street2 )
    total_fed_expenditures = models.BigIntegerField(
        "Total Federal Expenditures"
     description=docs.total_fed_expenditures )  # , max_length=12
    type_of_entity = models.CharField("Contact FAC for information", max_length=40, description=docs.type_of_entity )
    type_report_financial_statements = models.CharField(
        "Type of Report Issued on the Financial Statements", max_length=40, null=True,
     description=docs.type_report_financial_statements )
    type_report_major_program = models.CharField(
        "Type of Report Issued on the Major Program Compliance",
        max_length=40,
        null=True,
     description=docs.type_report_major_program_general )
    type_report_special_purpose_framework = models.CharField(
        "The auditor's opinion on the special purpose framework",
        max_length=40,
        null=True,
     description=docs.type_report_special_purpose_framework )
    uei = models.CharField("Unique Entity ID", max_length=12, description=docs.uei_general )
    zip_code = models.IntegerField("Auditee Zipcode" description=docs.zip_code )  # , max_length=9


class CfdaInfo(models.Model):
    research_and_development = models.BooleanField(
        "Indicate whether or not the program is a Research and Development program",
        null=True,
     description=docs.research_and_development )
    loans = models.BooleanField(
        "Indicate whether or not the program is a Loan or Loan Guarantee (only available for audit years 2013 and beyond)",
        null=True,
     description=docs.loans )
    arra = models.BooleanField(
        "American Recovery and Reinvestment Act Funded Program", null=True
     description=docs.arra )
    direct = models.BooleanField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        null=True,
     description=docs.direct )
    passthrough_award = models.BooleanField(
        "Indicates whether or not funds were passed through to any subrecipients for the Federal program",
        null=True,
     description=docs.passthrough_award )
    major_program = models.BooleanField(
        "Indicate whether or not the Federal program is a major program", null=True,
     description=docs.major_program )
    finding_ref_nums = models.CharField(
        "Findings Reference Numbers", max_length=100, null=True
     description=docs.finding_ref_nums_cfdainfo )
    amount = models.BigIntegerField(
        "Amount Expended for the Federal Program"
     description=docs.amount )  # , max_length=12
    program_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension"
     description=docs.program_total )  # , max_length=12
    cluster_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name"
     description=docs.cluster_total )  # , max_length=12
    passthrough_amount = models.BigIntegerField(
        "Amount passed through to subrecipients", null=True
     description=docs.passthrough_amount )  # , max_length=12
    loan_balance = models.CharField(
        "The loan or loan guarantee (loan) balance outstanding at the end of the audit period.  A response of ‘N/A’ is acceptable.",
        max_length=40,
        null=True,
     description=docs.loan_balance )
    federal_program_name = models.CharField("Name of Federal Program", max_length=300, description=docs.federal_program_name )
    cfda_program_name = models.CharField(
        "Name of Federal Program (auto-generated by FAC from the CFDA catalog)",
        max_length=300,
     description=docs.cfda_program_name )
    award_identification = models.CharField(
        "Other data used to identify the award which is not a CFDA number (e.g., program year, contract number)",
        max_length=50,
     description=docs.award_identification )
    # can have letters
    cfda = models.CharField("Federal Agency Prefix and Extension", max_length=52 description=docs.cfda )
    cluster_name = models.CharField("The name of the cluster", max_length=75, null=True, description=docs.cluster_name )
    state_cluster_name = models.CharField(
        "The name of the state cluster", max_length=75, null=True,
     description=docs.state_cluster_name )
    other_cluster_name = models.CharField(
        "The name of the cluster (if not listed in the Compliance Supplement)",
        max_length=75,
        null=True,
     description=docs.other_cluster_name )
    type_requirement = models.CharField(
        "Type Requirement Failure", max_length=40, null=True,
     description=docs.type_requirement_cfdainfo )
    type_report_major_program = models.CharField(
        "Type of Report Issued on the Major Program Compliance", max_length=40,
     description=docs.type_report_major_program_cfdainfo )
    # not in key for this table check descriptions
    findings = models.TextField("Items on the Findings page", null=True, description=docs.findings )
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)"
     description=docs.findings_count )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings"
     description=docs.elec_audits_id_cfdainfo )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_cfdainfo )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_cfdainfo )
    ## needs sources ##
    ein = models.IntegerField(
        "Primary Employer Identification Number")  # , max_length=9
    ## needs documentation ##
    # check this- it is QCOSTS2
    questioned_costs = models.CharField(
        "Questioned Costs",
        null=True,
        max_length=40,
    )


class Findings(models.Model):
    modified_opinion = models.BooleanField("Modified Opinion finding", null=True, description=docs.modified_opinion )
    other_non_compliance = models.BooleanField("Other Noncompliance finding", null=True, description=docs.other_non_compliance )
    material_weakness = models.BooleanField("Material Weakness finding", null=True, description=docs.material_weakness_findings )
    significant_deficiency = models.BooleanField(
        "Significant Deficiency finding", null=True,
     description=docs.significant_deficiency )
    other_findings = models.BooleanField("Other findings", null=True, description=docs.other_findings )
    questioned_costs = models.BooleanField("Questioned Costs", null=True, description=docs.questioned_costs_findings )
    repeat_finding = models.BooleanField(
        "Indicates whether or not the audit finding was a repeat of an audit finding in the immediate prior audit",
        null=True,
     description=docs.repeat_finding )
    finding_ref_nums = models.CharField("Findings Reference Numbers", max_length=100 description=docs.finding_ref_nums_findings )
    prior_finding_ref_nums = models.CharField(
        "Audit finding reference numbers from the immediate prior audit", max_length=100,
     description=docs.prior_finding_ref_nums )
    type_requirement = models.CharField("Type Requirement Failure", max_length=40,description=docs.type_requirement_findings )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings"
     description=docs.elec_audits_id_findings )
    elec_audit_findings_id = models.IntegerField(
        "FAC system generated sequence number for finding"
     description=docs.elec_audit_findings_id )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_findings )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_findings )


class Findingstext(models.Model):
    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
     description=docs.charts_tables_findingstext )
    finding_ref_nums = models.CharField(
        "Audit Finding Reference Number", max_length=100,
     description=docs.finding_ref_nums_findingstext )
    seq_number = models.IntegerField(
        "Order that the findings text was reported"
     description=docs.seq_number_findingstext )  # , max_length=4
    text = models.TextField("Content of the finding text" description=docs.text_findingstext )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_findingstext )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_findingstext )


class Captext(models.Model):
    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
     description=docs.charts_tables_captext )
    finding_ref_nums = models.CharField(
        "Audit Finding Reference Number", max_length=100
     description=docs.finding_ref_nums_captext )
    seq_number = models.IntegerField(
        "Order that the CAP text was reported"
     description=docs.seq_number_captext )  # , max_length=4
    text = models.TextField("Content of the Corrective Action Plan (CAP)" description=docs.text_captext )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_captext )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_captext )


class Notes(models.Model):
    type_id = models.CharField("Note Type", max_length=1, description=docs.type_id )
    fac_id = models.IntegerField(
        "Internal Unique Identifier for the record"
     description=docs.fac_id )  # , max_length=12
    report_id = models.IntegerField("Internal Audit Report Id" description=docs.report_id )  # , max_length=12
    version = models.IntegerField("Internal Version" description=docs.version )  # , max_length=4
    seq_number = models.IntegerField(
        "Order that the Note was reported"
     description=docs.seq_number_notes )  # , max_length=4
    note_index = models.IntegerField("Display Index for the Note" description=docs.note_index )  # , max_length=4
    content = models.TextField("Content of the Note" description=docs.content )
    title = models.CharField("Note Title", max_length=75, description=docs.title )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_notes )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_notes )


class MultipleCpasInfo(models.Model):
    cpa_phone = models.PositiveBigIntegerField(
        "CPA phone number",
        null=True,
     description=docs.cpa_phone_multiplecpasinfo )  # , max_length=10
    cpa_fax = models.PositiveBigIntegerField(
        "CPA fax number (optional)",
        null=True,
     description=docs.cpa_fax_multiplecpasinfo )  # , max_length=10
    cpa_state = models.CharField("CPA State", max_length=2, description=docs.cpa_state_multiplecpasinfo )
    cpa_city = models.CharField("CPA City", max_length=30, description=docs.cpa_city_multiplecpasinfo )
    cpa_title = models.CharField("Title of CPA Contact", max_length=40, description=docs.cpa_title_multiplecpasinfo)
    cpa_street1 = models.CharField("CPA Street Address", max_length=45, description=docs.cpa_street1_multiplecpasinfo )
    # no cpa_street2 ?
    cpa_zip_code = models.IntegerField(
        "CPA Zip Code",
        null=True,
     description=docs.cpa_zip_code_multiplecpasinfo )  # , max_length=9
    cpa_contact = models.CharField("Name of CPA Contact", max_length=50, description=docs.cpa_contact_multiplecpasinfo )
    cpa_email = models.CharField(
        "CPA mail address (optional)",
        max_length=60,
        null=True,
     description=docs.cpa_email_multiplecpasinfo )
    cpa_firm_name = models.CharField("CPA Firm Name", max_length=64, description=docs.cpa_firm_name_multiplecpasinfo )
    cpa_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        null=True,
     description=docs.cpa_ein )  # , max_length=9
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_multiplecpasinfo )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_multiplecpasinfo )
    seqnum = models.IntegerField(
        "Order that Auditors were reported on page 5 of SF-SAC", null=True
     description=docs.seqnum )


class Revisions(models.Model):
    findings = models.CharField(
        "Indicates what items on the Findings page were edited during the revision",
        max_length=110,
     description=docs.findings )
    elec_report_revision_id = models.IntegerField(
        "Internal Unique Identifier for the record"
     description=docs.elec_report_revision_id )  # , max_length=12
    federal_awards = models.CharField(
        "Indicates what items on the Federal Awards page were edited during the revision",
        max_length=140,
     description=docs.federal_awards )
    general_info_explain = models.CharField(
        "Explanation of what items on the General Info page were edited during the revision",
        max_length=150,
     description=docs.general_info_explain )
    federal_awards_explain = models.TextField(
        "Explanation of what items on the Federal Awards page were edited during the revision",
     description=docs.federal_awards_explain )
    notes_to_sefa_explain = models.TextField(
        "Explanation of what items on the Notes to SEFA page were edited during the revision",
     description=docs.notes_to_sefa_expalin )
    auditinfo_explain = models.TextField(
        "Explanation of what items on the Audit Info page were edited during the revision",
     description=docs.auditinfo_explain )
    findings_explain = models.TextField(
        "Explanation of what items on the Findings page were edited during the revision",
     description=docs.findings_explain )
    findings_text_explain = models.TextField(
        "Explanation of what items on the Text of the Audit Findings page were edited during the revision",
     description=docs.findings_text_explain )
    cap_explain = models.TextField(
        "Explanation of what items on the CAP Text page were edited during the revision",
     description=docs.cap_explain )
    other_explain = models.TextField(
        "Explanation of what other miscellaneous items were edited during the revision",
     description=docs.other_explain )
    audit_info = models.CharField(
        "Indicates what items on the Audit Info page were edited during the revision",
        max_length=200,
     description=docs.audit_info )
    notes_to_sefa = models.CharField(
        "Indicates what items on the Notes to SEFA page were edited during the revision",
        max_length=50,
     description=docs.notes_to_sefa )
    findings_text = models.CharField(
        "Indicates what items on the Text of the Audit Findings page were edited during the revision",
        max_length=6,
     description=docs.findings_text )
    cap = models.CharField(
        "Indicates what items on the CAP Text page were edited during the revision",
        max_length=6,
     description=docs.cap )
    other = models.CharField(
        "Indicates what other miscellaneous items were edited during the revision",
        max_length=65,
     description=docs.other )
    general_info = models.CharField(
        "Indicates what items on the General Info page were edited during the revision",
        max_length=75,
     description=docs.general_info )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_revisions )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_revisions )


class UeiInfo(models.Model):
    uei = models.CharField("Multiple Unique Entity Identifier Numbers", max_length=12, description=docs.uei_ueiinfo )
    uei_seq_num = models.IntegerField(
        "Order that UEI was reported on page 4 of SF-SAC"
     description=docs.uei_seq_num )  # , max_length=40
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_ueiinfo )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_ueiinfo )


class Agencies(models.Model):
    agency_cfda = models.IntegerField(
        "2-digit prefix of Federal Agency requiring copy of audit report",
     description=docs.agency_cfda )  # , max_length=2
    ein = models.IntegerField(
        "Employer Identification Number (EIN) of primary grantee", null=True
     description=docs.ein_agencies )  # , max_length=9
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_agencies )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_agencies )


class Passthrough(models.Model):
    passthrough_name = models.CharField("Name of Pass-through Entity", max_length=70, description=docs.passthrough_name )
    passthrough_id = models.CharField(
        "Identifying Number Assigned by the Pass-through Entity", max_length=70,
     description=docs.passthrough_id )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Passthrough data between CFDA Info and Passthrough"
     description=docs.elec_audits_id_passthrough )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key",
        max_length=40,
     description=docs.audit_year_passthrough )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key",
        max_length=40,
     description=docs.dbkey_passthrough )


class EinInfo(models.Model):
    ein = models.IntegerField(
        "Multiple Employer Identification Numbers"
     description=docs.ein_eininfo )  # , max_length=9
    ein_seq_num = models.IntegerField(
        "Order that EINs were reported on page 4 of SF-SAC"
     description=docs.ein_seq_num )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_eininfo )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_eininfo )


class DunsInfo(models.Model):
    duns = models.IntegerField(
        "Multiple Data Universal Numbering System Numbers"
     description=docs.duns_dunsinfo )  # , max_length=9
    duns_seq_num = models.IntegerField(
        "Order that DUNS was reported on page 4 of SF-SAC"
     description=docs.duns_seq_num )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.dbkey_dunsinfo )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
     description=docs.audit_year_dunsinfo )
