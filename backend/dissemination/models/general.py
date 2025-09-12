from django.db import models

from audit.models.constants import RESUBMISSION_STATUS_CHOICES
from .constants import REPORT_ID_FK_HELP_TEXT
from dissemination.models import docs


class General(models.Model):
    # Relational fields
    # null = True for these so we can load in phases, may want to tighten validation later
    # 20240125 - These are indices that would be used in our ALN search/annotation.
    # class Meta:
    #     indexes = [
    #         models.Index(fields=["report_id",]),
    #         models.Index(fields=["fac_accepted_date",]),

    #     ]

    # NOTE: This list was pulled from the `summary_reports.py` file. It is the list of fields we
    # export as part of the SF-SAC XLSX download.
    HASH_FIELDS = [
        "agencies_with_prior_findings",
        "audit_period_covered",
        "audit_type",
        "audit_year",
        "auditee_address_line_1",
        "auditee_certified_date",
        "auditee_certify_name",
        "auditee_certify_title",
        "auditee_city",
        "auditee_contact_name",
        "auditee_contact_title",
        "auditee_ein",
        "auditee_email",
        "auditee_name",
        "auditee_phone",
        "auditee_state",
        "auditee_uei",
        "auditee_zip",
        "auditor_address_line_1",
        "auditor_certified_date",
        "auditor_certify_name",
        "auditor_certify_title",
        "auditor_city",
        "auditor_contact_name",
        "auditor_contact_title",
        "auditor_country",
        "auditor_ein",
        "auditor_email",
        "auditor_firm_name",
        "auditor_foreign_address",
        "auditor_phone",
        "auditor_state",
        "auditor_zip",
        "cognizant_agency",
        "data_source",
        "dollar_threshold",
        "entity_type",
        "fac_accepted_date",
        "fy_end_date",
        "fy_start_date",
        "gaap_results",
        "is_additional_ueis",
        "is_aicpa_audit_guide_included",
        "is_going_concern_included",
        "is_internal_control_deficiency_disclosed",
        "is_internal_control_material_weakness_disclosed",
        "is_low_risk_auditee",
        "is_material_noncompliance_disclosed",
        "is_public",
        "is_sp_framework_required",
        "number_months",
        "oversight_agency",
        "report_id",
        "sp_framework_basis",
        "sp_framework_opinions",
        "total_amount_expended",
        "type_audit_code",
        # 20250912 MCJ: Because of the off-by-one issues in timezones, it might be best
        # to leave these out of the hash until those issues are resolved. Or, figure out what is
        # going on that the hashing is happening before the timezone issue, because (somehow)
        # the hash is being computed before the data changes and hits the dissem tables.
        # "date_created",
        # "ready_for_certification_date",
        # "submitted_date",
    ]

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
    # auditor_signature_date = models.DateField(
    #     "The date on which the auditor signed the audit",
    # )
    # auditee_signature_date = models.DateField(
    #     "The date on which the auditee signed the audit",
    # )
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
    # is_duplicate_reports = models.BooleanField(
    #     "Whether or not the financial statements include departments that have separate expenditures not included in this audit",
    #     null=True,
    #     help_text=docs.dup_reports,
    # )  # is_aicpa_audit_guide_included
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
    # FIXME This looks like audit_report_type in FederalAwards, must be verified
    #  and removed if needed.
    # type_report_major_program = models.TextField(
    #     "Type of Report Issued on the Major Program Compliance",
    #     null=True,
    #     help_text=docs.type_report_major_program_general,
    # )

    # Resubmission Status
    resubmission_status = models.CharField(
        max_length=30,
        choices=RESUBMISSION_STATUS_CHOICES,
        default=None,
        null=True,
    )

    # Resubmission Version
    resubmission_version = models.BigIntegerField(
        default=0,
        help_text="Version counter of how many times this SAC was resubmitted.",
    )
    hash = models.CharField(
        help_text="A hash of the row",
        blank=True,
        null=True,
    )

    class Meta:
        unique_together = (("report_id",),)

    def __str__(self):
        return (
            f"report_id:{self.report_id} UEI:{self.auditee_uei}, AY:{self.audit_year}"
        )
