# importing django models and users
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

from data_distro import docs  # noqa


# New models
class Auditee(models.Model):
    auditee_certify_name = models.CharField(
        "Name of Auditee Certifying Official",
        max_length=50,
        null=True,
        help_text=docs.auditee_certify_name,
    )
    auditee_certify_title = models.CharField(
        "Title of Auditee Certifying Official",
        max_length=50,
        null=True,
        help_text=docs.auditee_certify_title,
    )
    auditee_contact = models.CharField(
        "Name of Auditee Contact", max_length=50, help_text=docs.auditee_contact
    )
    auditee_email = models.CharField(
        "Auditee Email address",
        max_length=60,
        null=True,
        help_text=docs.auditee_email,
    )
    auditee_fax = models.PositiveBigIntegerField(
        "Auditee Fax Number (optional)", null=True, help_text=docs.auditee_fax
    )
    auditee_name = models.CharField(
        "Name of the Auditee", max_length=70, help_text=docs.auditee_name
    )
    auditee_name_title = models.CharField(
        "Title of Auditee Certifying Official",
        max_length=70,
        help_text=docs.auditee_name_title,
    )
    auditee_phone = models.PositiveBigIntegerField(
        "Auditee Phone Number", help_text=docs.auditee_phone
    )
    auditee_title = models.CharField(
        "Title of Auditee Contact", max_length=40, help_text=docs.auditee_title
    )
    street1 = models.CharField(
        "Auditee Street Address", max_length=45, help_text=docs.street1
    )
    street2 = models.CharField(
        "Auditee Street Address", max_length=45, null=True, help_text=docs.street2
    )
    city = models.CharField("Auditee City", max_length=30, help_text=docs.city)
    state = models.CharField("Auditee State", max_length=2, help_text=docs.state)
    # double check both of these are for the auditee
    ein = models.IntegerField(
        "Primary Employer Identification Number", help_text=docs.ein_general
    )  # , max_length=9
    ein_subcode = models.IntegerField(
        "Subcode assigned to the EIN", null=True, help_text=docs.ein_subcode
    )  # , max_length=3
    zip_code = models.CharField(
        "Auditee Zip Code",
        max_length=12,
        help_text=docs.zip_code,
    )  # , max_length=9
    duns_list = ArrayField(
        models.IntegerField(
            "Multiple Data Universal Numbering System Numbers, an array of DUNS numbers of the Auditee.",
            help_text=docs.duns_general,
        ),
    )
    uei_list = ArrayField(
        models.CharField("Unique Entity ID", max_length=12, help_text=docs.uei_general),
    )
    is_public = models.BooleanField("True if appears in a public record")


class Auditor(models.Model):
    cpa_phone = models.PositiveBigIntegerField(
        "CPA phone number", null=True, help_text=docs.cpa_phone_multiplecpasinfo
    )  # , max_length=10
    cpa_fax = models.PositiveBigIntegerField(
        "CPA fax number (optional)",
        null=True,
        help_text=docs.cpa_fax_multiplecpasinfo,
    )  # , max_length=10
    cpa_state = models.CharField(
        "CPA State", max_length=2, help_text=docs.cpa_state_multiplecpasinfo
    )
    cpa_city = models.CharField(
        "CPA City", max_length=30, help_text=docs.cpa_city_multiplecpasinfo
    )
    cpa_title = models.CharField(
        "Title of CPA Contact",
        max_length=40,
        help_text=docs.cpa_title_multiplecpasinfo,
    )
    cpa_street1 = models.CharField(
        "CPA Street Address",
        max_length=45,
        help_text=docs.cpa_street1_multiplecpasinfo,
    )
    cpa_street2 = models.CharField(
        "CPA Street Address",
        max_length=45,
        null=True,
        help_text=docs.cpa_street1_multiplecpasinfo,
    )
    cpa_zip_code = models.CharField(
        "CPA Zip Code", null=True, max_length=12, help_text=docs.cpa_zip_code_multiplecpasinfo
    )
    cpa_country = models.CharField(
        "CPA Country", max_length=6, null=True, help_text=docs.cpa_country
    )
    cpa_contact = models.CharField(
        "Name of CPA Contact",
        max_length=50,
        help_text=docs.cpa_contact_multiplecpasinfo,
    )
    cpa_email = models.CharField(
        "CPA mail address (optional)",
        max_length=60,
        null=True,
        help_text=docs.cpa_email_multiplecpasinfo,
    )
    cpa_firm_name = models.CharField(
        "CPA Firm Name", max_length=64, help_text=docs.cpa_firm_name_multiplecpasinfo
    )
    cpa_foreign = models.CharField(
        "CPA Address - if international",
        max_length=200,
        null=True,
        help_text=docs.cpa_foreign,
    )
    cpa_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.cpa_ein,
    )  # , max_length=9
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_multiplecpasinfo,
    )
    auditor_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        help_text=docs.auditor_ein,
    )

    seqnum = models.IntegerField(
        "Order that Auditors were reported on page 5 of SF-SAC",
        null=True,
        help_text=docs.seqnum,
    )
    is_public = models.BooleanField("True if appears in a public record")


class CfdaInfo(models.Model):
    research_and_development = models.BooleanField(
        "Indicate whether or not the program is a Research and Development program",
        null=True,
        help_text=docs.research_and_development,
    )
    loans = models.BooleanField(
        "Indicate whether or not the program is a Loan or Loan Guarantee (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.loans,
    )
    arra = models.BooleanField(
        "American Recovery and Reinvestment Act Funded Program",
        null=True,
        help_text=docs.arra,
    )
    direct = models.BooleanField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        null=True,
        help_text=docs.direct,
    )
    passthrough_award = models.BooleanField(
        "Indicates whether or not funds were passed through to any subrecipients for the Federal program",
        null=True,
        help_text=docs.passthrough_award,
    )
    major_program = models.BooleanField(
        "Indicate whether or not the Federal program is a major program",
        null=True,
        help_text=docs.major_program,
    )
    finding_ref_nums = models.CharField(
        "Findings Reference Numbers",
        max_length=100,
        null=True,
        help_text=docs.finding_ref_nums_cfdainfo,
    )
    amount = models.BigIntegerField(
        "Amount Expended for the Federal Program", help_text=docs.amount
    )  # , max_length=12
    program_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension",
        help_text=docs.program_total,
    )  # , max_length=12
    cluster_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name",
        help_text=docs.cluster_total,
    )  # , max_length=12
    passthrough_amount = models.BigIntegerField(
        "Amount passed through to subrecipients",
        null=True,
        help_text=docs.passthrough_amount,
    )  # , max_length=12
    loan_balance = models.CharField(
        "The loan or loan guarantee (loan) balance outstanding at the end of the audit period.  A response of ‘N/A’ is acceptable.",
        max_length=40,
        null=True,
        help_text=docs.loan_balance,
    )
    federal_program_name = models.CharField(
        "Name of Federal Program", max_length=300, help_text=docs.federal_program_name
    )
    cfda_program_name = models.CharField(
        "Name of Federal Program (auto-generated by FAC from the CFDA catalog)",
        max_length=300,
        help_text=docs.cfda_program_name,
    )
    award_identification = models.CharField(
        "Other data used to identify the award which is not a CFDA number (e.g., program year, contract number)",
        max_length=50,
        help_text=docs.award_identification,
    )
    # can have letters
    cfda = models.CharField(
        "Federal Agency Prefix and Extension", max_length=52, help_text=docs.cfda
    )
    cluster_name = models.CharField(
        "The name of the cluster",
        max_length=75,
        null=True,
        help_text=docs.cluster_name,
    )
    state_cluster_name = models.CharField(
        "The name of the state cluster",
        max_length=75,
        null=True,
        help_text=docs.state_cluster_name,
    )
    other_cluster_name = models.CharField(
        "The name of the cluster (if not listed in the Compliance Supplement)",
        max_length=75,
        null=True,
        help_text=docs.other_cluster_name,
    )
    type_requirement = models.CharField(
        "Type Requirement Failure",
        max_length=40,
        null=True,
        help_text=docs.type_requirement_cfdainfo,
    )
    type_report_major_program = models.CharField(
        "Type of Report Issued on the Major Program Compliance",
        max_length=40,
        help_text=docs.type_report_major_program_cfdainfo,
    )
    # not in key for this table check descriptions
    findings = models.TextField(
        "Items on the Findings page", null=True, help_text=docs.findings
    )
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)",
        help_text=docs.findings_count,
    )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings",
        help_text=docs.elec_audits_id_cfdainfo,
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_cfdainfo,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_cfdainfo,
    )
    ## needs sources ##
    ein = models.IntegerField(
        "Primary Employer Identification Number",
    )  # , max_length=9
    ## needs documentation ##
    # check this- it is QCOSTS2
    questioned_costs = models.CharField(
        "Questioned Costs",
        null=True,
        max_length=40,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class FindingsText(models.Model):
    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
        help_text=docs.charts_tables_findingstext,
    )
    finding_ref_nums = models.CharField(
        "Audit Finding Reference Number",
        max_length=100,
        help_text=docs.finding_ref_nums_findingstext,
    )
    seq_number = models.IntegerField(
        "Order that the findings text was reported",
        help_text=docs.seq_number_findingstext,
    )  # , max_length=4
    text = models.TextField(
        "Content of the finding text", help_text=docs.text_findingstext
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_findingstext,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_findingstext,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class Findings(models.Model):
    findings_text = models.ForeignKey(FindingsText, on_delete=models.CASCADE, null=True)
    modified_opinion = models.BooleanField(
        "Modified Opinion finding", null=True, help_text=docs.modified_opinion
    )
    other_non_compliance = models.BooleanField(
        "Other Noncompliance finding", null=True, help_text=docs.other_non_compliance
    )
    material_weakness = models.BooleanField(
        "Material Weakness finding",
        null=True,
        help_text=docs.material_weakness_findings,
    )
    significant_deficiency = models.BooleanField(
        "Significant Deficiency finding",
        null=True,
        help_text=docs.significant_deficiency,
    )
    other_findings = models.BooleanField(
        "Other findings", null=True, help_text=docs.other_findings
    )
    questioned_costs = models.BooleanField(
        "Questioned Costs", null=True, help_text=docs.questioned_costs_findings
    )
    repeat_finding = models.BooleanField(
        "Indicates whether or not the audit finding was a repeat of an audit finding in the immediate prior audit",
        null=True,
        help_text=docs.repeat_finding,
    )
    finding_ref_nums = models.CharField(
        "Findings Reference Numbers",
        max_length=100,
        help_text=docs.finding_ref_nums_findings,
    )
    prior_finding_ref_nums = models.CharField(
        "Audit finding reference numbers from the immediate prior audit",
        max_length=100,
        help_text=docs.prior_finding_ref_nums,
    )
    type_requirement = models.CharField(
        "Type Requirement Failure",
        max_length=40,
        help_text=docs.type_requirement_findings,
    )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings",
        help_text=docs.elec_audits_id_findings,
    )
    elec_audit_findings_id = models.IntegerField(
        "FAC system generated sequence number for finding",
        help_text=docs.elec_audit_findings_id,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_findings,
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_findings,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class CapText(models.Model):
    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
        help_text=docs.charts_tables_captext,
    )
    finding_ref_nums = models.CharField(
        "Audit Finding Reference Number",
        max_length=100,
        help_text=docs.finding_ref_nums_captext,
    )
    seq_number = models.IntegerField(
        "Order that the CAP text was reported", help_text=docs.seq_number_captext
    )  # , max_length=4
    text = models.TextField(
        "Content of the Corrective Action Plan (CAP)", help_text=docs.text_captext
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_captext,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_captext,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class Notes(models.Model):
    type_id = models.CharField("Note Type", max_length=1, help_text=docs.type_id)
    fac_id = models.IntegerField(
        "Internal Unique Identifier for the record", help_text=docs.fac_id
    )  # , max_length=12
    report_id = models.IntegerField(
        "Internal Audit Report Id", help_text=docs.report_id
    )  # , max_length=12
    version = models.IntegerField(
        "Internal Version", help_text=docs.version
    )  # , max_length=4
    seq_number = models.IntegerField(
        "Order that the Note was reported", help_text=docs.seq_number_notes
    )  # , max_length=4
    note_index = models.IntegerField(
        "Display Index for the Note", help_text=docs.note_index
    )  # , max_length=4
    content = models.TextField("Content of the Note", help_text=docs.content)
    title = models.CharField("Note Title", max_length=75, help_text=docs.title)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_notes,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_notes,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class Revisions(models.Model):
    findings = models.CharField(
        "Indicates what items on the Findings page were edited during the revision",
        max_length=110,
        help_text=docs.findings,
    )
    elec_report_revision_id = models.IntegerField(
        "Internal Unique Identifier for the record",
        help_text=docs.elec_report_revision_id,
    )  # , max_length=12
    federal_awards = models.CharField(
        "Indicates what items on the Federal Awards page were edited during the revision",
        max_length=140,
        help_text=docs.federal_awards,
    )
    general_info_explain = models.CharField(
        "Explanation of what items on the General Info page were edited during the revision",
        max_length=150,
        help_text=docs.general_info_explain,
    )
    federal_awards_explain = models.TextField(
        "Explanation of what items on the Federal Awards page were edited during the revision",
        help_text=docs.federal_awards_explain,
    )
    notes_to_sefa_explain = models.TextField(
        "Explanation of what items on the Notes to SEFA page were edited during the revision",
        help_text=docs.notes_to_sefa_explain,
    )
    auditinfo_explain = models.TextField(
        "Explanation of what items on the Audit Info page were edited during the revision",
        help_text=docs.auditinfo_explain,
    )
    findings_explain = models.TextField(
        "Explanation of what items on the Findings page were edited during the revision",
        help_text=docs.findings_explain,
    )
    findings_text_explain = models.TextField(
        "Explanation of what items on the Text of the Audit Findings page were edited during the revision",
        help_text=docs.findings_text_explain,
    )
    cap_explain = models.TextField(
        "Explanation of what items on the CAP Text page were edited during the revision",
        help_text=docs.cap_explain,
    )
    other_explain = models.TextField(
        "Explanation of what other miscellaneous items were edited during the revision",
        help_text=docs.other_explain,
    )
    audit_info = models.CharField(
        "Indicates what items on the Audit Info page were edited during the revision",
        max_length=200,
        help_text=docs.audit_info,
    )
    notes_to_sefa = models.CharField(
        "Indicates what items on the Notes to SEFA page were edited during the revision",
        max_length=50,
        help_text=docs.notes_to_sefa,
    )
    findings_text = models.CharField(
        "Indicates what items on the Text of the Audit Findings page were edited during the revision",
        max_length=6,
        help_text=docs.findings_text,
    )
    cap = models.CharField(
        "Indicates what items on the CAP Text page were edited during the revision",
        max_length=6,
        help_text=docs.cap,
    )
    other = models.CharField(
        "Indicates what other miscellaneous items were edited during the revision",
        max_length=65,
        help_text=docs.other,
    )
    general_info = models.CharField(
        "Indicates what items on the General Info page were edited during the revision",
        max_length=75,
        help_text=docs.general_info,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_revisions,
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_revisions,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class Agencies(models.Model):
    agency_cfda = models.IntegerField(
        "2-digit prefix of Federal Agency requiring copy of audit report",
        help_text=docs.agency_cfda,
    )  # , max_length=2
    ein = models.IntegerField(
        "Employer Identification Number (EIN) of primary grantee",
        null=True,
        help_text=docs.ein_agencies,
    )  # , max_length=9

    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.dbkey_agencies,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_agencies,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class Passthrough(models.Model):
    passthrough_name = models.CharField(
        "Name of Pass-through Entity", max_length=70, help_text=docs.passthrough_name
    )
    passthrough_id = models.CharField(
        "Identifying Number Assigned by the Pass-through Entity",
        max_length=70,
        help_text=docs.passthrough_id,
    )
    elec_audits_id = models.IntegerField(
        "FAC system generated sequence number used to link to Passthrough data between CFDA Info and Passthrough",
        help_text=docs.elec_audits_id_passthrough,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key",
        max_length=40,
        help_text=docs.audit_year_passthrough,
    )
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key",
        max_length=40,
        help_text=docs.dbkey_passthrough,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class General(models.Model):
    # we may need null = True for these so we can load in phases
    auditee = models.ForeignKey(Auditee, on_delete=models.CASCADE, null=True)
    auditor = models.ManyToManyField(Auditor)
    cfda = models.ForeignKey(CfdaInfo, on_delete=models.CASCADE, null=True)
    findings = models.ForeignKey(Findings, on_delete=models.CASCADE, null=True)
    cap_text = models.ForeignKey(CapText, on_delete=models.CASCADE, null=True)
    notes = models.ForeignKey(Notes, on_delete=models.CASCADE, null=True)
    revisions = models.ForeignKey(Revisions, on_delete=models.CASCADE, null=True)
    passthrough = models.ForeignKey(Passthrough, on_delete=models.CASCADE, null=True)
    agency = models.ManyToManyField(Agencies)

    # need to verify what going on with agency fields
    cognizant_agency = models.CharField(
        "Two digit Federal agency prefix of the cognizant agency",
        max_length=2,
        null=True,
        help_text=docs.cognizant_agency,
    )
    ## needs documentation ##
    cognizant_agency_over = models.CharField(max_length=2, null=True)
    auditee_date_signed = models.DateField(
        "Date of Auditee signature", help_text=docs.auditee_date_signed
    )
    cpa_date_signed = models.DateField(
        "Date of CPA signature", help_text=docs.cpa_date_signed
    )
    audit_type = models.CharField(
        "Type of Audit",
        max_length=40,
        help_text=docs.audit_type,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_general,
    )
    completed_on = models.DateField(
        "Date the Audit was Posted to the Internet as Complete",
        null=True,
        help_text=docs.completed_on,
    )
    component_date_received = models.DateField(
        "The most recent date an audit component was received by the FAC. This field was not populated before 2004. Receipt of Financial statements only are not processed until the rest of the audit or a Form SF-SAC is also received.",
        null=True,
        help_text=docs.component_date_received,
    )
    condition_or_deficiency = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition/significant deficiency on financial statements",
        null=True,
        help_text=docs.condition_or_deficiency,
    )
    condition_or_deficiency_major_program = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition/significant deficiency for any major program in the Schedule of Findings and Questioned Costs",
        null=True,
        help_text=docs.condition_or_deficiency_major_program,
    )
    current_or_former_findings = models.BooleanField(
        "Indicate whether or not current year findings or prior year findings affecting direct funds were reported",
        null=True,
        help_text=docs.current_or_former_findings,
    )
    ## needs documentation ##
    date_firewall = models.DateField(null=True)
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key. Only on records created by census.",
        max_length=40,
        help_text=docs.dbkey_general,
    )
    dollar_threshold = models.FloatField(
        "Dollar Threshold to distinguish between Type A and Type B programs.",
        null=True,
        help_text=docs.dollar_threshold,
    )
    dup_reports = models.BooleanField(
        "Whether or not the financial statements include departments that have separate expenditures not included in this audit",
        null=True,
        help_text=docs.dup_reports,
    )

    entity_type = models.CharField(
        "Self reported type of entity (i.e., States, Local Governments, Indian Tribes, Institutions of Higher Education, NonProfit)",
        max_length=50,
        help_text=docs.entity_type,
    )
    fac_accepted_date = models.DateField(
        "The most recent date an audit report was submitted to the FAC that passed FAC screening and was accepted as a valid OMB Circular A-133 report submission.",
        help_text=docs.fac_accepted_date,
    )
    form_date_received = models.DateField(
        "The most Recent Date the Form SF-SAC was received by the FAC. This field was not populated before 2001.",
        null=True,
        help_text=docs.form_date_received,
    )
    fy_end_date = models.DateField("Fiscal Year End Date", help_text=docs.fy_end_date)
    fy_start_date = models.DateField(
        "Fiscal Year Start Date", null=True, help_text=docs.fy_start_date
    )
    going_concern = models.BooleanField(
        "Whether or not the audit contained a going concern paragraph on financial statements",
        null=True,
        help_text=docs.going_concern,
    )
    initial_date_received = models.DateField(
        "The first date an audit component or Form SF-SAC was received by the Federal audit Clearinghouse (FAC).",
        null=True,
        help_text=docs.initial_date_received,
    )
    low_risk = models.BooleanField(
        "Indicate whether or not the auditee qualified as a low-risk auditee",
        null=True,
        help_text=docs.low_risk,
    )
    material_noncompliance = models.BooleanField(
        "Whether or not the audit disclosed a material noncompliance on financial statements",
        null=True,
        help_text=docs.material_noncompliance,
    )
    material_weakness = models.BooleanField(
        "Whether or not the audit disclosed any reportable condition/significant deficiency as a material weakness on financial statements",
        null=True,
        help_text=docs.material_weakness_general,
    )
    material_weakness_major_program = models.BooleanField(
        "Indicate whether any reportable condition/signficant deficiency was disclosed as a material weakness for a major program in the Schedule of Findings and Questioned Costs",
        null=True,
        help_text=docs.material_weakness_major_program,
    )
    number_months = models.IntegerField(
        "Number of Months Covered by the 'Other' Audit Period",
        null=True,
        help_text=docs.number_months,
    )
    oversight_agency = models.IntegerField(
        "Two digit Federal agency prefix of the oversight agency",
        null=True,
        help_text=docs.oversight_agency,
    )  # , max_length=2
    period_covered = models.CharField(
        "Audit Period Covered by Audit", max_length=40, help_text=docs.period_covered
    )
    previous_completed_on = models.DateField(
        "Date the Audit was Previously Posted to the Internet as Complete",
        null=True,
        help_text=docs.previous_completed_on,
    )
    ### needs documentation ###
    previous_date_firewall = models.DateField(null=True)
    prior_year_schedule = models.BooleanField(
        "Indicate whether or not the report includes a Summary Schedule of Prior Year Audit Findings",
        null=True,
        help_text=docs.prior_year_schedule,
    )
    questioned_costs = models.BooleanField(
        "Indicate whether or not the audit disclosed any known questioned costs.",
        null=True,
        help_text=docs.questioned_costs_general,
    )
    report_required = models.BooleanField(
        "Distribution to Federal Agency required?",
        null=True,
        help_text=docs.report_required,
    )
    sp_framework = models.CharField(
        "Special Purpose Framework that was used as the basis of accounting",
        max_length=40,
        null=True,
        help_text=docs.sp_framework,
    )
    sp_framework_required = models.BooleanField(
        "Indicate whether or not the special purpose framework used as basis of accounting by state law or tribal law",
        null=True,
        help_text=docs.sp_framework_required,
    )
    total_fed_expenditures = models.BigIntegerField(
        "Total Federal Expenditures", help_text=docs.total_fed_expenditures
    )  # , max_length=12
    type_of_entity = models.CharField(
        "Contact FAC for information", max_length=40, help_text=docs.type_of_entity
    )
    type_report_financial_statements = models.CharField(
        "Type of Report Issued on the Financial Statements",
        max_length=40,
        null=True,
        help_text=docs.type_report_financial_statements,
    )
    type_report_major_program = models.CharField(
        "Type of Report Issued on the Major Program Compliance",
        max_length=40,
        null=True,
        help_text=docs.type_report_major_program_general,
    )
    type_report_special_purpose_framework = models.CharField(
        "The auditor's opinion on the special purpose framework",
        max_length=40,
        null=True,
        help_text=docs.type_report_special_purpose_framework,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )
    # might want to add meta data to other models too, but everything eventually links back here, so this is good enough for now
    modified_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    data_source = models.CharField("Origin of the upload", max_length=25)
