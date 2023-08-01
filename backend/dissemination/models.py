from django.db import models
from django.contrib.postgres.fields import ArrayField

from . import docs


class FindingText(models.Model):
    """Specific findings details. References General"""

    report_id = models.CharField(
        "G-FAC generated identifier.l",
        max_length=40,
    )
    finding_ref_number = models.CharField(
        "Finding Reference Number - FK",
        max_length=100,
        null=True,
        help_text=docs.finding_ref_nums_findingstext,
    )
    contains_chart_or_table = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
        help_text=docs.charts_tables_findingstext,
    )
    finding_text = models.TextField(
        "Content of the finding text",
        null=True,
        help_text=docs.text_findingstext,
    )

    class Meta:
        unique_together = (
            (
                "report_id",
                "finding_ref_number",
            ),
        )
        """
            FindingText
            foreign_key(("report_id", ) references General
        """


class Finding(models.Model):
    """A finding from the audit. References FederalAward and FindingText"""

    award_reference = models.CharField(
        "Order that the award line was reported in Award",
        null=True,
    )
    report_id = models.CharField(
        "G-FAC generated identifier. FK along with other fields - refers to Award",
        max_length=40,
    )
    finding_seq_number = models.IntegerField(
        "Order that the finding line was reported",
        null=True,
    )
    finding_ref_number = models.CharField(
        "Findings Reference Numbers",
        max_length=100,
        unique=True,
        help_text=docs.finding_ref_nums_findings,
    )
    is_material_weakness = models.BooleanField(
        "Material Weakness finding",
        null=True,
        help_text=docs.material_weakness_findings,
    )
    is_modified_opinion = models.BooleanField(
        "Modified Opinion finding", null=True, help_text=docs.modified_opinion
    )
    is_other_findings = models.BooleanField(
        "Other findings", null=True, help_text=docs.other_findings
    )
    is_other_non_compliance = models.BooleanField(
        "Other non-compliance", null=True, help_text=docs.other_non_compliance
    )
    # each element in the list is a FK to Finding
    prior_finding_ref_numbers = models.CharField(
        "Audit finding reference numbers from the immediate prior audit",
        max_length=100,
        help_text=docs.prior_finding_ref_nums,
        null=True,
    )
    is_questioned_costs = models.BooleanField(
        "Questioned Costs", null=True, help_text=docs.questioned_costs_findings
    )
    is_repeat_finding = models.BooleanField(
        "Indicates whether or not the audit finding was a repeat of an audit finding in the immediate prior audit",
        null=True,
        help_text=docs.repeat_finding,
    )
    is_significant_deficiency = models.BooleanField(
        "Significant Deficiency finding",
        null=True,
        help_text=docs.significant_deficiency_findings,
    )
    type_requirement = models.CharField(
        "Type Requirement Failure",
        max_length=40,
        null=True,
        help_text=docs.type_requirement_findings,
    )

    class Meta:
        unique_together = (("report_id", "award_reference", "finding_seq_number"),)
        """
            Finding
            foreign_key(("report_id", "award_reference",) references FederalAward
            foreign_key(("report_id", "finding_ref_number",) references FindingText
        """


class FederalAward(models.Model):
    """Information about the federal award section of the form. References General"""

    report_id = models.CharField(
        "G-FAC generated identifier. FK refers to a General",
        max_length=40,
    )

    award_reference = models.CharField(
        "Order that the award line was reported", default=-1
    )

    federal_agency_prefix = models.CharField(
        "2-char code refers to an agency",
        max_length=2,
    )
    federal_award_extension = models.CharField(
        "3-digit extn for a program defined by the agency",
        max_length=3,
    )
    additional_award_identification = models.CharField(
        "Other data used to identify the award which is not a CFDA number (e.g., program year, contract number)",
        max_length=50,
        null=True,
        help_text=docs.award_identification,
    )
    federal_program_name = models.TextField(
        "Name of Federal Program",
        null=True,
        help_text=docs.federal_program_name,
    )
    amount_expended = models.BigIntegerField(
        "Amount Expended for the Federal Program", help_text=docs.amount
    )
    cluster_name = models.TextField(
        "The name of the cluster",
        null=True,
        help_text=docs.cluster_name,
    )
    other_cluster_name = models.TextField(
        "The name of the cluster (if not listed in the Compliance Supplement)",
        null=True,
        help_text=docs.other_cluster_name,
    )
    state_cluster_name = models.TextField(
        "The name of the state cluster",
        null=True,
        help_text=docs.state_cluster_name,
    )
    cluster_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same Cluster Name",
        null=True,
        help_text=docs.cluster_total,
    )
    federal_program_total = models.BigIntegerField(
        "Total Federal awards expended for each individual Federal program is auto-generated by summing the amount expended for all line items with the same CFDA Prefix and Extension",
        null=True,
        help_text=docs.program_total,
    )
    is_loan = models.BooleanField(
        "Indicate whether or not the program is a Loan or Loan Guarantee (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.loans,
    )
    loan_balance = models.DecimalField(
        "The loan or loan guarantee (loan) balance outstanding at the end of the audit period.  A response of ‘N/A’ is acceptable.",
        null=True,
        max_digits=10,
        decimal_places=2,
        help_text=docs.loan_balance,
    )
    is_direct = models.BooleanField(
        "Indicate whether or not the award was received directly from a Federal awarding agency",
        null=True,
        help_text=docs.direct,
    )

    is_major = models.BooleanField(
        "Indicate whether or not the Federal program is a major program",
        null=True,
        help_text=docs.major_program,
    )
    mp_audit_report_type = models.CharField(
        "Type of Report Issued on the Major Program Compliance",
        max_length=40,
        null=True,
        help_text=docs.type_report_major_program_cfdainfo,
    )
    findings_count = models.IntegerField(
        "Number of findings for the federal program (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.findings_count,
    )

    is_passthrough_award = models.BooleanField(
        "Indicates whether or not funds were passed through to any subrecipients for the Federal program",
        null=True,
        help_text=docs.passthrough_award,
    )
    passthrough_name = models.TextField(
        "If no (Direct Award), Name of Passthrough Entity",
        null=True,
    )
    passthrough_id = models.TextField(
        "If no (Direct Award), Identifying Number Assigned by the Pass-through Entity, if assigned",
        null=True,
    )
    passthrough_amount = models.BigIntegerField(
        "Amount passed through to subrecipients",
        null=True,
        help_text=docs.passthrough_amount,
    )
    type_requirement = models.CharField(
        "Type Requirement Failure",
        max_length=40,
        null=True,
        help_text=docs.type_requirement_cfdainfo,
    )

    class Meta:
        unique_together = (
            (
                "report_id",
                "award_reference",
            ),
        )
        """
            FederalAward
            foreign_key(("report_id", ) references General

        """


class CapText(models.Model):
    """Corrective action plan text. Referebces General"""

    report_id = models.CharField(
        "G-FAC generated identifier. FK refers to a General",
        max_length=40,
    )
    finding_ref_number = models.CharField(
        "Audit Finding Reference Number",
        max_length=100,
        help_text=docs.finding_ref_nums_captext,
    )
    contains_chart_or_table = models.BooleanField(
        "Indicates whether or not the text contained charts or tables that could not be entered due to formatting restrictions",
        max_length=1,
        null=True,
        help_text=docs.charts_tables_captext,
    )
    planned_action = models.TextField(
        "Content of the Corrective Action Plan (CAP)", help_text=docs.text_captext
    )

    class Meta:
        unique_together = (
            (
                "report_id",
                "finding_ref_number",
            ),
        )
        """
            CapText
            foreign_key(("report_id", ) references General
        """


class Note(models.Model):
    """Note to Schedule of Expenditures of Federal Awards (SEFA)"""

    report_id = models.CharField(
        "G-FAC generated identifier. FK refers to a General",
        max_length=40,
    )
    note_seq_number = models.IntegerField(
        "Order that the Note was reported", help_text=docs.seq_number_notes
    )
    content = models.TextField("Content of the Note", null=True, help_text=docs.content)
    note_title = models.TextField("Note Title", null=True, help_text=docs.title)
    accounting_policies = models.TextField(null=True)
    is_minimis_rate_used = models.CharField(max_length=3, null=True)
    rate_explained = models.TextField(null=True)

    class Meta:
        unique_together = (("report_id", "note_seq_number"),)
        """
            Note
            foreign_key(("report_id", ) references General
        """


class Revision(models.Model):
    """Documents what was revised on the associated form from the previous version"""

    findings = models.TextField(
        "Indicates what items on the Findings page were edited during the revision",
        null=True,
        help_text=docs.findings_revisions,
    )
    revision_id = models.IntegerField(
        "Internal Unique Identifier for the record",
        null=True,
        help_text=docs.elec_report_revision_id,
    )
    federal_awards = models.TextField(
        "Indicates what items on the Federal Awards page were edited during the revision",
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
    audit_info = models.TextField(
        "Indicates what items on the Audit Info page were edited during the revision",
        null=True,
        help_text=docs.audit_info,
    )
    notes_to_sefa = models.TextField(
        "Indicates what items on the Notes to Schedule of Expenditures of Federal Awards (SEFA) page were edited during the revision",
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
    other = models.TextField(
        "Indicates what other miscellaneous items were edited during the revision",
        null=True,
        help_text=docs.other,
    )
    general_info = models.TextField(
        "Indicates what items on the General Info page were edited during the revision",
        null=True,
        help_text=docs.general_info,
    )
    audit_year = models.IntegerField(
        "Audit year from fy_start_date",
        help_text=docs.audit_year_revisions,
    )
    report_id = models.CharField(
        "G-FAC generated identifier. FK refers to General",
        max_length=40,
    )


class Passthrough(models.Model):
    """The pass-through entity information, when it is not a direct federal award"""

    """
    We may not need this table. We can simply add three columns
    pertating to passthrough in FederalAward table
    """
    award_reference = models.CharField(
        "Order that the award line was reported",
        null=True,
    )
    report_id = models.CharField(
        "G-FAC generated identifier. FK refers to General",
        max_length=40,
    )
    # This doesn't seem like it should be null but it is sometimes
    passthrough_id = models.CharField(
        "Identifying Number Assigned by the Pass-through Entity",
        max_length=70,
        null=True,
        help_text=docs.passthrough_id,
    )
    passthrough_name = models.TextField(
        "Name of Pass-through Entity",
        null=True,
        help_text=docs.passthrough_name,
    )

    class Meta:
        unique_together = (("report_id", "award_reference", "passthrough_id"),)
        """
            Note
            foreign_key(("report_id", ) references General
        """


class General(models.Model):
    # Relational fields
    # null = True for these so we can load in phases, may want to tighten validation later

    report_id = models.CharField(
        "G-FAC generated identifier. ",
        max_length=40,
        unique=True,
    )
    auditee_certify_name = models.TextField(
        "Name of Auditee Certifying Official",
        null=True,
        help_text=docs.auditee_certify_name,
    )
    auditee_certify_title = models.TextField(
        "Title of Auditee Certifying Official",
        null=True,
        help_text=docs.auditee_certify_title,
    )
    auditee_contact_name = models.TextField(
        "Name of Auditee Contact",
        null=True,
        help_text=docs.auditee_contact,
    )
    auditee_email = models.CharField(
        "Auditee Email address",
        max_length=254,
        null=True,
        help_text=docs.auditee_email,
    )
    auditee_name = models.TextField("Name of the Auditee", help_text=docs.auditee_name)
    auditee_phone = models.TextField(
        "Auditee Phone Number", help_text=docs.auditee_phone
    )
    auditee_contact_title = models.TextField(
        "Title of Auditee Contact",
        null=True,
        help_text=docs.auditee_title,
    )
    auditee_address_line_1 = models.TextField(
        "Auditee Street Address", help_text=docs.street1
    )
    auditee_city = models.TextField("Auditee City", help_text=docs.city)
    auditee_state = models.CharField(
        "Auditee State", max_length=2, help_text=docs.state
    )
    auditee_ein = models.CharField(
        "Primary Employer Identification Number",
        null=True,
        max_length=30,
    )
    auditee_uei = models.CharField(
        "", max_length=30, null=True, help_text=docs.uei_general
    )
    auditee_addl_uei_list = ArrayField(
        models.CharField("", null=True, help_text=docs.uei_general), default=list
    )
    auditee_zip = models.CharField(
        "Auditee Zip Code",
        max_length=12,
        null=True,
        help_text=docs.zip_code,
    )
    auditor_phone = models.TextField(
        "CPA phone number", null=True, help_text=docs.auditor_phone
    )
    auditor_state = models.CharField(
        "CPA State", max_length=2, null=True, help_text=docs.auditor_state
    )
    auditor_city = models.TextField("CPA City", null=True, help_text=docs.auditor_city)
    auditor_contact_title = models.TextField(
        "Title of CPA Contact",
        max_length=40,
        null=True,
        help_text=docs.auditor_title,
    )
    auditor_address_line_1 = models.TextField(
        "CPA Street Address",
        max_length=45,
        null=True,
        help_text=docs.auditor_street1,
    )
    auditor_zip = models.CharField(
        "CPA Zip Code",
        null=True,
        max_length=12,
        help_text=docs.auditor_zip_code,
    )
    auditor_country = models.CharField(
        "CPA Country", max_length=45, null=True, help_text=docs.auditor_country
    )
    auditor_contact_name = models.TextField(
        "Name of CPA Contact",
        null=True,
        help_text=docs.auditor_contact,
    )
    auditor_email = models.CharField(
        "CPA mail address (optional)",
        max_length=254,
        null=True,
        help_text=docs.auditor_email,
    )
    auditor_firm_name = models.TextField(
        "CPA Firm Name", help_text=docs.auditor_firm_name
    )
    # Once loaded, would like to add these as regular addresses and just change this to a country field
    auditor_foreign_addr = models.TextField(
        "CPA Address - if international",
        null=True,
        help_text=docs.auditor_foreign,
    )
    auditor_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.auditor_ein,
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

    # Dates
    initial_date_received = models.DateField(
        "The first date an audit component or Form SF-SAC was received by the Federal audit Clearinghouse (FAC).",
        null=True,
        help_text=docs.initial_date_received,
    )
    ready_for_certification_date = models.DateField(
        "The date at which the audit transitioned to 'ready for certification'",
        null=True,
    )
    auditor_certified_date = models.DateField(
        "The date at which the audit transitioned to 'auditor certified'", null=True
    )
    auditee_certified_date = models.DateField(
        "The date at which the audit transitioned to 'auditee certified'", null=True
    )
    certified_date = models.DateField(
        "The date at which the audit transitioned to 'certified'", null=True
    )
    submitted_date = models.DateField(
        "The date at which the audit transitioned to 'submitted'", null=True
    )
    auditor_signature_date = models.DateField(
        "The date on which the auditor signed the audit", null=True
    )
    auditee_signature_date = models.DateField(
        "The date on which the auditee signed the audit", null=True
    )
    fy_end_date = models.DateField(
        "Fiscal Year End Date", null=True, help_text=docs.fy_end_date
    )
    fy_start_date = models.DateField(
        "Fiscal Year Start Date", null=True, help_text=docs.fy_start_date
    )
    audit_year = models.IntegerField(
        "Audit year from fy_start_date.",
        help_text=docs.audit_year_general,
    )

    audit_type = models.CharField(
        "Type of Audit",
        max_length=40,
        help_text=docs.audit_type,
    )

    # Audit Info
    gaap_results = models.TextField(
        "GAAP Results by Auditor",
        null=True,
    )  # Concatenation of choices
    sp_framework = models.CharField(
        "Special Purpose Framework that was used as the basis of accounting",
        max_length=40,
        null=True,
        help_text=docs.sp_framework,
    )
    is_sp_framework_required = models.BooleanField(
        "Indicate whether or not the special purpose framework used as basis of accounting by state law or tribal law",
        null=True,
        help_text=docs.sp_framework_required,
    )
    sp_framework_auditor_opinion = models.CharField(
        "The auditor's opinion on the special purpose framework",
        max_length=40,
        null=True,
        help_text=docs.type_report_special_purpose_framework,
    )
    is_going_concern = models.BooleanField(
        "Whether or not the audit contained a going concern paragraph on financial statements",
        null=True,
        help_text=docs.going_concern,
    )
    is_significant_deficiency = models.BooleanField(
        "Whether or not the audit disclosed a significant deficiency on financial statements",
        null=True,
        help_text=docs.significant_deficiency_general,
    )
    is_material_weakness = models.BooleanField(
        "", null=True, help_text=docs.material_weakness_general
    )
    is_material_noncompliance = models.BooleanField(
        "Whether or not the audit disclosed a material noncompliance on financial statements",
        null=True,
        help_text=docs.material_noncompliance,
    )
    is_duplicate_reports = models.BooleanField(
        "Whether or not the financial statements include departments that have separate expenditures not included in this audit",
        null=True,
        help_text=docs.dup_reports,
    )  # is_aicpa_audit_guide_included
    dollar_threshold = models.DecimalField(
        "Dollar Threshold to distinguish between Type A and Type B programs.",
        null=True,
        max_digits=10,
        decimal_places=2,
        help_text=docs.dollar_threshold,
    )
    is_low_risk = models.BooleanField(
        "Indicate whether or not the auditee qualified as a low-risk auditee",
        null=True,
        help_text=docs.low_risk,
    )
    agencies_with_prior_findings = models.TextField(
        "List of agencues with prior findings",
        null=True,
    )  # Concatenation of agency codes
    # End of Audit Info

    entity_type = models.CharField(
        "Self reported type of entity (i.e., States, Local Governments, Indian Tribes, Institutions of Higher Education, NonProfit)",
        max_length=50,
        null=True,
        help_text=docs.entity_type,
    )
    number_months = models.IntegerField(
        "Number of Months Covered by the 'Other' Audit Period",
        null=True,
        help_text=docs.number_months,
    )
    audit_period_covered = models.CharField(
        "Audit Period Covered by Audit", max_length=40, help_text=docs.period_covered
    )
    report_required = models.BooleanField(
        "Distribution to Federal Agency required?",
        null=True,
        help_text=docs.report_required,
    )

    total_fed_expenditures = models.BigIntegerField(
        "Total Federal Expenditures",
        null=True,
        help_text=docs.total_fed_expenditures,
    )
    type_report_major_program = models.CharField(
        "Type of Report Issued on the Major Program Compliance",
        max_length=40,
        null=True,
        help_text=docs.type_report_major_program_general,
    )
    type_audit_code = models.CharField("Determines if audit is A133 or UG", default="")

    # Metadata
    is_public = models.BooleanField(
        "True for public records, False for non-public records", null=True
    )
    # Choices are: C-FAC and G-FAC
    data_source = models.CharField("Origin of the upload", max_length=25)

    class Meta:
        unique_together = (("report_id",),)
        """
            General
            The root of the submission tree
        """

    def __str__(self):
        return f"Id:{self.report_id} UEI:{self.auditee_uei}, AY2x:{self.audit_year}"


class SecondaryAuditor(models.Model):
    report_id = models.CharField(
        "G-FAC generated identifier. FK to General",
        max_length=40,
    )
    auditor_seq_number = models.IntegerField("Order that the Auditor was reported")
    auditor_ein = models.IntegerField(
        "CPA Firm EIN (only available for audit years 2013 and beyond)",
        null=True,
        help_text=docs.auditor_ein,
    )
    auditor_name = models.TextField("CPA Firm Name", help_text=docs.auditor_firm_name)
    contact_name = models.TextField(
        "Name of CPA Contact",
        null=True,
    )
    contact_title = models.TextField(
        "Title of CPA Contact",
        null=True,
        help_text=docs.auditor_title,
    )
    contact_email = models.CharField(
        "CPA mail address (optional)",
        max_length=254,
        null=True,
        help_text=docs.auditor_email,
    )
    contact_phone = models.TextField(
        "CPA phone number", null=True, help_text=docs.auditor_phone
    )
    address_street = models.TextField(
        "CPA Street Address",
        null=True,
        help_text=docs.auditor_street1,
    )
    address_city = models.CharField(
        "CPA City", max_length=30, null=True, help_text=docs.auditor_city
    )
    address_state = models.CharField(
        "CPA State", max_length=2, null=True, help_text=docs.auditor_state
    )
    address_zipcode = models.CharField(
        "CPA Zip Code",
        null=True,
        max_length=12,
        help_text=docs.auditor_zip_code,
    )

    class Meta:
        unique_together = (("report_id", "auditor_seq_number"),)
        """
            SecondaryAuditor
            Secindary and additional auditors
            foreign_key(("report_id", ) references General

       """
