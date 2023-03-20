from django.db import models
from django.contrib.postgres.fields import ArrayField

from data_distro import docs


# Will refactor
class Agency(models.Model):
    """Information about the Agency requiring a copy of the audit"""

    # can we separate extensions?
    agency_aln = models.CharField(
        "Assistance Listing Number (ALN), a 2-digit prefix of Federal Agency",
        null=True,
        max_length=40,
    )
    agency_cfda = models.IntegerField(
        "Catalog of Federal Domestic Assistance (CFDA) code, a 2-digit prefix of Federal Agency requiring copy of audit.",
        null=True,
        # need to update docs
        help_text=docs.agency_cfda,
    )
    agency_name = models.CharField(
        "Name of the Federal Agency requiring copy of audit report",
        null=True,
        max_length=125,
    )
    federal_program_name = models.CharField(
        "Name of Federal Program",
        max_length=300,
        null=True,
        help_text=docs.federal_program_name,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class Auditee(models.Model):
    """Information about the entity undergoing the audit"""

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
        "Name of Auditee Contact",
        max_length=50,
        null=True,
        help_text=docs.auditee_contact,
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
        null=True,
        help_text=docs.auditee_name_title,
    )
    auditee_phone = models.PositiveBigIntegerField(
        "Auditee Phone Number", help_text=docs.auditee_phone
    )
    auditee_title = models.CharField(
        "Title of Auditee Contact",
        max_length=40,
        null=True,
        help_text=docs.auditee_title,
    )
    auditee_street1 = models.CharField(
        "Auditee Street Address", max_length=45, help_text=docs.street1
    )
    auditee_street2 = models.CharField(
        "Auditee Street Address", max_length=45, null=True, help_text=docs.street2
    )
    auditee_city = models.CharField("Auditee City", max_length=30, help_text=docs.city)
    auditee_state = models.CharField(
        "Auditee State", max_length=2, help_text=docs.state
    )
    ein_list = ArrayField(
        models.IntegerField(
            "Primary Employer Identification Number, in the order that they were listed.",
            null=True,
            help_text=docs.ein_list,
        )
    )
    ein_subcode = models.IntegerField(
        "Subcode assigned to the EIN.", null=True, help_text=docs.ein_subcode
    )
    auditee_zip_code = models.CharField(
        "Auditee Zip Code",
        max_length=12,
        null=True,
        help_text=docs.zip_code,
    )
    duns_list = ArrayField(
        models.IntegerField(
            "Multiple Data Universal Numbering System Numbers (DUNS) of the Auditee, in the order they were listed.",
            null=True,
            help_text=docs.duns_list,
        ),
    )
    uei_list = ArrayField(
        models.CharField(
            "Unique Entity ID", max_length=12, null=True, help_text=docs.uei_general
        ),
    )
    is_public = models.BooleanField("True if appears in a public record")


class Auditor(models.Model):
    """Information about the Auditing CPA firm conducting the audit"""

    cpa_phone = models.PositiveBigIntegerField(
        "CPA phone number", null=True, help_text=docs.cpa_phone
    )
    cpa_fax = models.PositiveBigIntegerField(
        "CPA fax number (optional)",
        null=True,
        help_text=docs.cpa_fax,
    )
    cpa_state = models.CharField(
        "CPA State", max_length=2, null=True, help_text=docs.cpa_state
    )
    cpa_city = models.CharField(
        "CPA City", max_length=30, null=True, help_text=docs.cpa_city
    )
    cpa_title = models.CharField(
        "Title of CPA Contact",
        max_length=40,
        null=True,
        help_text=docs.cpa_title,
    )
    cpa_street1 = models.CharField(
        "CPA Street Address",
        max_length=45,
        null=True,
        help_text=docs.cpa_street1,
    )
    cpa_street2 = models.CharField(
        "CPA Street Address, line 2",
        max_length=45,
        null=True,
        help_text=docs.cpa_street2,
    )
    cpa_zip_code = models.CharField(
        "CPA Zip Code",
        null=True,
        max_length=12,
        help_text=docs.cpa_zip_code,
    )
    cpa_country = models.CharField(
        "CPA Country", max_length=6, null=True, help_text=docs.cpa_country
    )
    cpa_contact = models.CharField(
        "Name of CPA Contact",
        max_length=50,
        null=True,
        help_text=docs.cpa_contact,
    )
    cpa_email = models.CharField(
        "CPA mail address (optional)",
        max_length=60,
        null=True,
        help_text=docs.cpa_email,
    )
    cpa_firm_name = models.CharField(
        "CPA Firm Name", max_length=64, help_text=docs.cpa_firm_name
    )
    # Once loaded, would like to add these as regular addresses and just change this to a country field
    cpa_foreign = models.CharField(
        "CPA Address - if international",
        max_length=200,
        null=True,
        help_text=docs.cpa_foreign,
    )
    cpa_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.auditor_ein,
    )
    seqence_number = models.IntegerField(
        "Order that Auditors were reported on page 5 of SF-SAC (only for secondary_auditors)",
        null=True,
        help_text=docs.seqnum,
    )
    is_public = models.BooleanField("True if appears in a public record")


class FindingText(models.Model):
    """Specific findings details"""

    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
        help_text=docs.charts_tables_findingstext,
    )
    finding_ref_number = models.CharField(
        "Audit Finding Reference Number",
        max_length=100,
        null=True,
        help_text=docs.finding_ref_nums_findingstext,
    )
    seqence_number = models.IntegerField(
        "Order that the findings text was reported",
        null=True,
        help_text=docs.seq_number_findingstext,
    )
    text = models.TextField(
        "Content of the finding text",
        null=True,
        help_text=docs.text_findingstext,
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


class Finding(models.Model):
    """A finding from the audit"""

    findings_text = models.ManyToManyField(FindingText)
    finding_ref_number = models.CharField(
        "Findings Reference Numbers",
        max_length=100,
        help_text=docs.finding_ref_nums_findings,
    )
    audit_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings",
        help_text=docs.elec_audits_id_findings,
    )
    audit_findings_id = models.IntegerField(
        "FAC system generated sequence number for finding",
        help_text=docs.elec_audit_findings_id,
    )
    prior_finding_ref_numbers = models.CharField(
        "Audit finding reference numbers from the immediate prior audit",
        max_length=100,
        help_text=docs.prior_finding_ref_nums,
        null=True,
    )
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
        help_text=docs.significant_deficiency_findings,
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
    type_requirement = models.CharField(
        "Type Requirement Failure",
        max_length=40,
        null=True,
        help_text=docs.type_requirement_findings,
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


class FederalAward(models.Model):
    """Information about the federal award section of the form"""

    findings = models.ManyToManyField(Finding)
    audit_id = models.IntegerField(
        "FAC system generated sequence number used to link to Findings data between CFDA Info and Findings",
        help_text=docs.elec_audits_id_cfdainfo,
    )
    # this would be better as a list
    finding_ref_numbers = models.CharField(
        "Findings Reference Numbers",
        max_length=100,
        null=True,
        help_text=docs.finding_ref_nums_cfdainfo,
    )
    agency_prior_findings_list = ArrayField(
        models.IntegerField(
            "Federal Agencies with Current or Prior Year Audit Findings on Direct Awards. An empty list means None.",
            null=True,
            help_text=docs.agency_prior_findings,
        ),
        null=True,
    )
    # Agency
    federal_program_name = models.CharField(
        "Name of Federal Program",
        max_length=300,
        null=True,
        help_text=docs.federal_program_name,
    )
    agency_name = models.CharField(
        "Name of Federal Program (auto-generated by FAC from the CFDA catalog)",
        max_length=300,
        null=True,
        help_text=docs.cfda_program_name,
    )
    # can have letters
    agency_cfda = models.CharField(
        "Federal Agency Prefix and Extension", max_length=52, help_text=docs.cfda
    )
    award_identification = models.CharField(
        "Other data used to identify the award which is not a CFDA number (e.g., program year, contract number)",
        max_length=50,
        null=True,
        help_text=docs.award_identification,
    )
    # this is redundant, we could remove in the future, keeping for now so relationships can be verified
    cpa_ein = models.IntegerField(
        "Primary Employer Identification Number",
        null=True,
        help_text=docs.auditor_ein,
    )
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
    amount = models.BigIntegerField(
        "Amount Expended for the Federal Program", help_text=docs.amount
    )
    program_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension",
        null=True,
        help_text=docs.program_total,
    )
    cluster_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name",
        null=True,
        help_text=docs.cluster_total,
    )
    passthrough_amount = models.BigIntegerField(
        "Amount passed through to subrecipients",
        null=True,
        help_text=docs.passthrough_amount,
    )
    loan_balance = models.CharField(
        "The loan or loan guarantee (loan) balance outstanding at the end of the audit period.  A response of ‘N/A’ is acceptable.",
        max_length=40,
        null=True,
        help_text=docs.loan_balance,
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
        null=True,
        help_text=docs.type_report_major_program_cfdainfo,
    )
    findings_page = models.TextField(
        "Items on the Findings page", null=True, help_text=docs.findings
    )
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.findings_count,
    )
    questioned_costs = models.CharField(
        "Dollar amount of questioned costs (Deprecated since 2002)",
        null=True,
        max_length=40,
        help_text=docs.questioned_costs_FederalAward,
    )

    # metadata
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
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )


class CapText(models.Model):
    """Corrective action plan text"""

    finding_ref_number = models.CharField(
        "Audit Finding Reference Number",
        max_length=100,
        help_text=docs.finding_ref_nums_captext,
    )
    charts_tables = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
        help_text=docs.charts_tables_captext,
    )
    sequence_number = models.IntegerField(
        "Order that the CAP text was reported", help_text=docs.seq_number_captext
    )
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


class Note(models.Model):
    """Note to Schedule of Expenditures of Federal Awards (SEFA)"""

    type_id = models.CharField("Note Type", max_length=1, help_text=docs.type_id)
    fac_id = models.IntegerField(
        "Internal Unique Identifier for the record", help_text=docs.fac_id
    )
    report_id = models.IntegerField(
        "Internal Audit Report Id", help_text=docs.report_id
    )
    version = models.IntegerField("Internal Version", help_text=docs.version)
    sequence_number = models.IntegerField(
        "Order that the Note was reported", help_text=docs.seq_number_notes
    )
    note_index = models.IntegerField(
        "Display Index for the Note",
        null=True,
        help_text=docs.note_index,
    )
    content = models.TextField("Content of the Note", null=True, help_text=docs.content)
    title = models.CharField(
        "Note Title", max_length=75, null=True, help_text=docs.title
    )
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


class Revision(models.Model):
    """Documents what was revised on the associated form from the previous version"""

    findings = models.CharField(
        "Indicates what items on the Findings page were edited during the revision",
        max_length=110,
        null=True,
        help_text=docs.findings_revisions,
    )
    revision_id = models.IntegerField(
        "Internal Unique Identifier for the record",
        null=True,
        help_text=docs.elec_report_revision_id,
    )
    federal_awards = models.CharField(
        "Indicates what items on the Federal Awards page were edited during the revision",
        max_length=140,
        null=True,
        help_text=docs.federal_awards,
    )
    general_info_explain = models.TextField(
        "Explanation of what items on the General Info page were edited during the revision",
        null=True,
        help_text=docs.general_info_explain,
    )
    federal_awards_explain = models.TextField(
        "Explanation of what items on the Federal Awards page were edited during the revision",
        null=True,
        help_text=docs.federal_awards_explain,
    )
    notes_to_sefa_explain = models.TextField(
        "Explanation of what items on the Notes to Schedule of Expenditures of Federal Awards (SEFA) page were edited during the revision",
        null=True,
        help_text=docs.notes_to_sefa_explain,
    )
    audit_info_explain = models.TextField(
        "Explanation of what items on the Audit Info page were edited during the revision",
        null=True,
        help_text=docs.auditinfo_explain,
    )
    findings_explain = models.TextField(
        "Explanation of what items on the Findings page were edited during the revision",
        null=True,
        help_text=docs.findings_explain,
    )
    findings_text_explain = models.TextField(
        "Explanation of what items on the Text of the Audit Findings page were edited during the revision",
        null=True,
        help_text=docs.findings_text_explain,
    )
    cap_explain = models.TextField(
        "Explanation of what items on the CAP Text page were edited during the revision",
        null=True,
        help_text=docs.cap_explain,
    )
    other_explain = models.TextField(
        "Explanation of what other miscellaneous items were edited during the revision",
        null=True,
        help_text=docs.other_explain,
    )
    audit_info = models.CharField(
        "Indicates what items on the Audit Info page were edited during the revision",
        max_length=200,
        null=True,
        help_text=docs.audit_info,
    )
    notes_to_sefa = models.CharField(
        "Indicates what items on the Notes to Schedule of Expenditures of Federal Awards (SEFA) page were edited during the revision",
        max_length=50,
        null=True,
        help_text=docs.notes_to_sefa,
    )
    findings_text = models.CharField(
        "Indicates what items on the Text of the Audit Findings page were edited during the revision",
        max_length=6,
        null=True,
        help_text=docs.findings_text,
    )
    cap = models.CharField(
        "Indicates what items on the CAP Text page were edited during the revision",
        max_length=6,
        null=True,
        help_text=docs.cap,
    )
    other = models.CharField(
        "Indicates what other miscellaneous items were edited during the revision",
        max_length=65,
        null=True,
        help_text=docs.other,
    )
    general_info = models.CharField(
        "Indicates what items on the General Info page were edited during the revision",
        max_length=75,
        null=True,
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


class Passthrough(models.Model):
    """The pass-through entity information, when it is not a direct federal award"""

    passthrough_name = models.CharField(
        "Name of Pass-through Entity",
        max_length=150,
        null=True,
        help_text=docs.passthrough_name,
    )
    # This doesn't seem like it should be null but it is sometimes
    passthrough_id = models.CharField(
        "Identifying Number Assigned by the Pass-through Entity",
        max_length=70,
        null=True,
        help_text=docs.passthrough_id,
    )
    audit_id = models.IntegerField(
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
    """Data from the General Info and Audit Info forms with links to other parts of the form"""

    # Relational fields
    # null = True for these so we can load in phases, may want to tighten validation later
    auditee = models.ForeignKey(Auditee, on_delete=models.CASCADE, null=True)
    primary_auditor = models.ForeignKey(
        Auditor,
        related_name="primary_auditor",
        on_delete=models.CASCADE,
        null=True,
    )
    secondary_auditors = models.ManyToManyField(
        Auditor,
        related_name="secondary_auditor",
    )
    federal_awards = models.ManyToManyField(FederalAward)
    findings = models.ManyToManyField(Finding)
    findings_text = models.ManyToManyField(FindingText)
    cap_text = models.ManyToManyField(CapText)
    notes = models.ManyToManyField(Note)
    passthrough = models.ManyToManyField(Passthrough)
    # We only have the most recent, so we only have one revision
    revision = models.ForeignKey(Revision, on_delete=models.CASCADE, null=True)
    pdf_urls = ArrayField(
        models.CharField("PDFs associated with the report", max_length=400, null=True),
        null=True,
    )

    # Agency
    cognizant_agency = models.CharField(
        "Two digit Federal agency prefix of the cognizant agency",
        max_length=2,
        null=True,
        help_text=docs.cognizant_agency,
    )
    oversight_agency = models.IntegerField(
        "Two digit Federal agency prefix of the oversight agency",
        null=True,
        help_text=docs.oversight_agency,
    )
    cognizant_agency_over = models.CharField(
        "A value of 'C' means the entity was assigned a Cognizant agency (had over $50 million in total expenses). A value of 'O' means the entity was assigned a Oversight agency (had less than $50 million in total expenses)",
        max_length=2,
        null=True,
        help_text=docs.cognizant_agency_over,
    )

    # Dates
    auditee_date_signed = models.DateField(
        "Date of Auditee signature", null=True, help_text=docs.auditee_date_signed
    )
    cpa_date_signed = models.DateField(
        "Date of CPA signature", null=True, help_text=docs.cpa_date_signed
    )
    date_published = models.DateField(
        "The date the audit information was made available on the dissemination site",
        null=True,
        help_text=docs.date_firewall,
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
    initial_date_received = models.DateField(
        "The first date an audit component or Form SF-SAC was received by the Federal audit Clearinghouse (FAC).",
        null=True,
        help_text=docs.initial_date_received,
    )
    fy_end_date = models.DateField(
        "Fiscal Year End Date", null=True, help_text=docs.fy_end_date
    )
    fy_start_date = models.DateField(
        "Fiscal Year Start Date", null=True, help_text=docs.fy_start_date
    )
    previous_completed_on = models.DateField(
        "Date the Audit was Previously Posted to the Internet as Complete",
        null=True,
        help_text=docs.previous_completed_on,
    )
    # This may all be nulls and we can get rid of it
    previous_date_published = models.DateField(
        null=True,
        help_text=docs.previous_date_firewall,
    )
    completed_date = models.DateField(
        "Date the Audit was Posted to the Internet as Complete",
        null=True,
        help_text=docs.completed_on,
    )
    component_date_received = models.DateField(
        "The most recent date an audit component was received by the FAC. This field was not populated before 2004. Receipt of Financial statements only are not processed until the rest of the audit or a Form SF-SAC is also received.",
        null=True,
        help_text=docs.component_date_received,
    )
    audit_year = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key.",
        max_length=40,
        help_text=docs.audit_year_general,
    )

    # Audit characteristics
    audit_type = models.CharField(
        "Type of Audit",
        max_length=40,
        help_text=docs.audit_type,
    )
    reportable_condition = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition on financial statements",
        null=True,
        help_text=docs.reportable_condition,
    )
    significant_deficiency = models.BooleanField(
        "Whether or not the audit disclosed a significant deficiency on financial statements",
        null=True,
        help_text=docs.significant_deficiency_general,
    )
    condition_or_deficiency_major_program = models.BooleanField(
        "Whether or not the audit disclosed a reportable condition/significant deficiency for any major program in the Schedule of Findings and Questioned Costs",
        null=True,
        help_text=docs.reportable_condition_major_program,
    )
    current_or_former_findings = models.BooleanField(
        "Indicate whether or not current year findings or prior year findings affecting direct funds were reported",
        null=True,
        help_text=docs.current_or_former_findings,
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
        null=True,
        help_text=docs.entity_type,
    )
    going_concern = models.BooleanField(
        "Whether or not the audit contained a going concern paragraph on financial statements",
        null=True,
        help_text=docs.going_concern,
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
        "Indicate whether any reportable condition/significant deficiency was disclosed as a material weakness for a major program in the Schedule of Findings and Questioned Costs",
        null=True,
        help_text=docs.material_weakness_major_program,
    )
    number_months = models.IntegerField(
        "Number of Months Covered by the 'Other' Audit Period",
        null=True,
        help_text=docs.number_months,
    )
    period_covered = models.CharField(
        "Audit Period Covered by Audit", max_length=40, help_text=docs.period_covered
    )
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
    special_framework = models.CharField(
        "Special Purpose Framework that was used as the basis of accounting",
        max_length=40,
        null=True,
        help_text=docs.sp_framework,
    )
    special_framework_required = models.BooleanField(
        "Indicate whether or not the special purpose framework used as basis of accounting by state law or tribal law",
        null=True,
        help_text=docs.sp_framework_required,
    )
    total_fed_expenditures = models.BigIntegerField(
        "Total Federal Expenditures",
        null=True,
        help_text=docs.total_fed_expenditures,
    )
    type_of_entity = models.CharField(
        "Contact FAC for information",
        max_length=40,
        null=True,
        help_text=docs.type_of_entity,
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

    # Metadata
    dbkey = models.CharField(
        "Audit Year and DBKEY (database key) combined make up the primary key. Only on records created by Census.",
        max_length=40,
        help_text=docs.dbkey_general,
    )
    is_public = models.BooleanField(
        "True for public records, False for non-public records"
    )
    # Might want to add meta data to other models too, but everything eventually links back here, so this is good enough for now
    modified_date = models.DateTimeField(auto_now=True)
    create_date = models.DateTimeField(auto_now_add=True)
    data_source = models.CharField("Origin of the upload", max_length=25)
