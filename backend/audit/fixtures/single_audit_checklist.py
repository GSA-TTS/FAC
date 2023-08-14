"""Fixtures for SingleAuditChecklist.

We want to create a variety of SACs in different states of
completion.
"""
from datetime import date, timedelta
import logging
import re
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker
import random
import uuid

from audit.excel import (
    extract_federal_awards,
    extract_findings_uniform_guidance,
    extract_findings_text,
    extract_corrective_action_plan,
    extract_secondary_auditors,
    extract_notes_to_sefa,
    extract_additional_ueis,
)
import audit.validators

from audit.fixtures.excel import FORM_SECTIONS
from users.models import User

logger = logging.getLogger(__name__)

from audit.management.commands.workbooks.base import dbkey_to_test_report_id
from audit.management.commands.census_models.ay22 import CensusGen22 as Gen

# TODO: Pull this from actual information.


def _fake_general_information(auditee_name=None):
    """Create a fake general_information object."""
    # TODO: can we generate this object from the schema definition in
    # schemas/output/GeneralInformation.schema.json?
    fake = Faker()
    general_information = {
        "auditee_fiscal_period_start": date.today().strftime("%Y-%m-%d"),
        "auditee_fiscal_period_end": (date.today() + timedelta(days=365)).strftime(
            "%Y-%m-%d"
        ),
        "audit_period_covered": "annual",
        "audit_type": "single-audit",
        "auditee_address_line_1": fake.street_address(),
        "auditee_city": fake.city(),
        "auditee_contact_name": fake.name(),
        "auditee_contact_title": fake.job(),
        "auditee_email": fake.ascii_email(),
        "auditee_name": auditee_name or fake.company(),
        "auditee_phone": fake.basic_phone_number(),
        # TODO: when we include territories in our valid states, remove this restriction
        "auditee_state": fake.state_abbr(include_territories=False),
        # TODO: this is GSA's UEI. We could do better at making random choices that
        # pass the schema's complex regex validation
        "auditee_uei": "DJ4KNQ383PH7",
        "auditee_zip": fake.postalcode(),
        "auditor_address_line_1": fake.street_address(),
        "auditor_city": fake.city(),
        "auditor_contact_name": fake.name(),
        "auditor_contact_title": fake.job(),
        "auditor_country": fake.country(),
        "auditor_ein": fake.ssn().replace("-", ""),
        "auditor_ein_not_an_ssn_attestation": True,
        "auditor_email": fake.ascii_email(),
        "auditor_firm_name": fake.company(),
        "auditor_phone": fake.basic_phone_number(),
        # TODO: when we include territories in our valid states, remove this restriction
        "auditor_state": fake.state_abbr(include_territories=False),
        "auditor_zip": fake.postalcode(),
        "ein": fake.ssn().replace("-", ""),
        "ein_not_an_ssn_attestation": True,
        "is_usa_based": True,
        "met_spending_threshold": True,
        "multiple_eins_covered": False,
        "multiple_ueis_covered": False,
        # TODO: could improve this by randomly choosing from the enum of possible values
        "user_provided_organization_type": "unknown",
    }

    # verify that our created object validates against the schema
    audit.validators.validate_general_information_json(general_information)

    return general_information


# TODO: Pull this from actual information.
def _fake_audit_information(auditee_name=None):
    audit_information = {
        "agencies": random.choices(list(range(0, 99)), k=random.randint(1, 8)),
        "dollar_threshold": random.randint(500000, 1000000),
        "gaap_results": random.choices(
            list(
                map(
                    lambda o: o["tag"],
                    [
                        {
                            "readable": "Unmodified opinion",
                            "tag": "unmodified_opinion",
                        },
                        {
                            "readable": "Qualified opinion",
                            "tag": "qualified_opinion",
                        },
                        {
                            "readable": "Adverse opinion",
                            "tag": "adverse_opinion",
                        },
                        {
                            "readable": "Disclaimer of opinion",
                            "tag": "disclaimer_of_opinion",
                        },
                        {
                            "readable": "Financial statements were not prepared in accordance with GAAP but were prepared in accordance with a special purpose framework.",
                            "tag": "not_gaap",
                        },
                    ],
                )
            ),
            k=random.randint(1, 4),
        ),
        "is_aicpa_audit_guide_included": random.choice([True, False]),
        "is_going_concern_included": random.choice([True, False]),
        "is_internal_control_deficiency_disclosed": random.choice([True, False]),
        "is_internal_control_material_weakness_disclosed": random.choice([True, False]),
        "is_low_risk_auditee": random.choice([True, False]),
        "is_material_noncompliance_disclosed": random.choice([True, False]),
    }
    return audit_information


def fake_auditor_certification():
    """Create fake auditor confirmation form data."""
    fake = Faker()
    data_step_1 = {
        "is_OMB_limited": True,
        "is_auditee_responsible": True,
        "has_used_auditors_report": True,
        "has_no_auditee_procedures": True,
        "is_FAC_releasable": True,
    }
    data_step_2 = {
        "auditor_name": fake.name(),
        "auditor_title": fake.job(),
        "auditor_certification_date_signed": fake.date(),
    }

    return data_step_1, data_step_2


def fake_auditee_certification():
    """Create fake auditor confirmation form data."""
    fake = Faker()
    data_step_1 = {
        "has_no_PII": True,
        "has_no_BII": True,
        "meets_2CFR_specifications": True,
        "is_2CFR_compliant": True,
        "is_complete_and_accurate": True,
        "has_engaged_auditor": True,
        "is_issued_and_signed": True,
        "is_FAC_releasable": True,
    }
    data_step_2 = {
        "auditee_name": fake.name(),
        "auditee_title": fake.job(),
        "auditee_certification_date_signed": fake.date(),
    }

    return data_step_1, data_step_2


def _create_test_sac(user, auditee_name, dbkey):
    """Create a single example SAC."""
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=_fake_general_information(auditee_name),
        audit_information=_fake_audit_information(auditee_name),
    )
    # Set a TEST report id for this data
    sac.report_id = dbkey_to_test_report_id(Gen, dbkey)
    sac.save()

    Access = apps.get_model("audit.Access")
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="editor",
    )
    # Why not give me all the access? This way, I can run the test all the way through!
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="certifying_auditee_contact",
    )
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="certifying_auditor_contact",
    )
    sac.data_source = "TEST DATA"

    logger.info("Created single audit checklist %s", sac)
    return sac


def _post_create_federal_awards(this_sac, this_user):
    """Upload a federal awards workbook for this SAC.

    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """
    ExcelFile = apps.get_model("audit.ExcelFile")

    if (
        ExcelFile.objects.filter(
            sac_id=this_sac.id, form_section=FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED
        ).exists()
        and this_sac.federal_awards is not None
    ):
        # there is already an uploaded file and data in the object so
        # nothing to do here
        return

    with open(
        settings.DATA_FIXTURES
        / "audit"
        / "excel_workbooks_test_files"
        / "federal-awards-workbook-PASS.xlsx",
        "rb",
    ) as f:
        content = f.read()
    file = SimpleUploadedFile("test.xlsx", content, "application/vnd.ms-excel")
    excel_file = ExcelFile(
        file=file,
        filename="temp",
        user=this_user,
        sac_id=this_sac.id,
        form_section=FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED,
    )
    excel_file.full_clean()
    excel_file.save()

    # TODO: refactor the upload handling from the post view into a
    # function so we can call it here instead of aping it.
    audit_data = audit.excel.extract_federal_awards(excel_file.file)
    audit.validators.validate_federal_award_json(audit_data)
    this_sac.federal_awards = audit_data
    this_sac.save()

    logger.info("Created Federal Awards workbook upload for SAC %s", this_sac.id)


def get_field_by_section(sac, section):
    if section == FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED:
        return sac.federal_awards
    elif section == FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE:
        return sac.findings_uniform_guidance
    elif section == FORM_SECTIONS.FINDINGS_TEXT:
        return sac.findings_text
    elif section == FORM_SECTIONS.CORRECTIVE_ACTION_PLAN:
        return sac.corrective_action_plan
    elif section == FORM_SECTIONS.SECONDARY_AUDITORS:
        return sac.secondary_auditors
    elif section == FORM_SECTIONS.NOTES_TO_SEFA:
        return sac.notes_to_sefa
    elif section == FORM_SECTIONS.ADDITIONAL_UEIS:
        return sac.additional_ueis


extract_mapping = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: extract_federal_awards,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: extract_findings_uniform_guidance,
    FORM_SECTIONS.FINDINGS_TEXT: extract_findings_text,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: extract_corrective_action_plan,
    FORM_SECTIONS.SECONDARY_AUDITORS: extract_secondary_auditors,
    FORM_SECTIONS.NOTES_TO_SEFA: extract_notes_to_sefa,
    FORM_SECTIONS.ADDITIONAL_UEIS: extract_additional_ueis,
}

validator_mapping = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: audit.validators.validate_federal_award_json,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: audit.validators.validate_findings_uniform_guidance_json,
    FORM_SECTIONS.FINDINGS_TEXT: audit.validators.validate_findings_text_json,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: audit.validators.validate_corrective_action_plan_json,
    FORM_SECTIONS.SECONDARY_AUDITORS: audit.validators.validate_secondary_auditors_json,
    FORM_SECTIONS.NOTES_TO_SEFA: audit.validators.validate_notes_to_sefa_json,
    FORM_SECTIONS.ADDITIONAL_UEIS: audit.validators.validate_additional_ueis_json,
    "PDF": audit.validators.validate_single_audit_report_file,
}


def _make_excel_file(filename, f_obj):
    content = f_obj.read()
    f_obj.seek(0)
    file = SimpleUploadedFile(filename, content, "application/vnd.ms-excel")
    return file


def _post_upload_workbook(this_sac, this_user, section, xlsx_file):
    """Upload a workbook for this SAC.

    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """
    ExcelFile = apps.get_model("audit.ExcelFile")

    if (
        ExcelFile.objects.filter(sac_id=this_sac.id, form_section=section).exists()
        and get_field_by_section(this_sac, section) is not None
    ):
        # there is already an uploaded file and data in the object so
        # nothing to do here
        return

    excel_file = ExcelFile(
        file=xlsx_file,
        filename=Path("xlsx.xlsx").stem,
        user=this_user,
        sac_id=this_sac.id,
        form_section=section,
    )
    excel_file.full_clean()
    excel_file.save()

    audit_data = extract_mapping[section](excel_file.file)
    validator_mapping[section](audit_data)

    if section == FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED:
        this_sac.federal_awards = audit_data
    elif section == FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE:
        this_sac.findings_uniform_guidance = audit_data
    elif section == FORM_SECTIONS.FINDINGS_TEXT:
        this_sac.findings_text = audit_data
    elif section == FORM_SECTIONS.CORRECTIVE_ACTION_PLAN:
        this_sac.corrective_action_plan = audit_data
    elif section == FORM_SECTIONS.SECONDARY_AUDITORS:
        this_sac.secondary_auditors = audit_data
    elif section == FORM_SECTIONS.NOTES_TO_SEFA:
        this_sac.notes_to_sefa = audit_data
    elif section == FORM_SECTIONS.ADDITIONAL_UEIS:
        this_sac.additional_ueis = audit_data

    this_sac.save()

    logger.info("Created Federal Awards workbook upload for SAC %s", this_sac.id)


# FIXME: It would be nice to:
# 1. Use a random number of pages between 20 and 500 from the CFR
# 2. Generate page numbers that are within that range
# Ideally, it would be in-memory. I'm not sure how to do that... yet...
def _post_upload_pdf(this_sac, this_user, pdf_filename):
    """Upload a workbook for this SAC.

    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """
    PDFFile = apps.get_model("audit.SingleAuditReportFile")

    if PDFFile.objects.filter(sac_id=this_sac.id).exists():
        # there is already an uploaded file and data in the object so
        # nothing to do here
        return

    with open(pdf_filename, "rb") as f:
        content = f.read()
    file = SimpleUploadedFile(pdf_filename, content, "application/pdf")
    print(file.__dict__)
    pdf_file = PDFFile(
        file=file,
        component_page_numbers={
            "financial_statements": 1,
            "financial_statements_opinion": 2,
            "schedule_expenditures": 3,
            "schedule_expenditures_opinion": 4,
            "uniform_guidance_control": 5,
            "uniform_guidance_compliance": 6,
            "GAS_control": 6,
            "GAS_compliance": 7,
            "schedule_findings": 8,
        },
        filename=Path(pdf_filename).stem,
        user=this_user,
        sac_id=this_sac.id,
    )

    validator_mapping["PDF"](pdf_file.file)

    pdf_file.full_clean()
    pdf_file.save()

    this_sac.save()

    logger.info("Uploaded audit report SAC %s", this_sac.id)


# list of the default SingleAuditChecklists to create for each user
# The auditee name is used to disambiguate them, so it must be unique
# or another SAC won't be created.
# If `post_create_callable` exists for an item, it should be a
# callable(sac, user) that does further processing after the SAC
# is created.
SACS = [
    {"auditee_name": "SAC in progress"},
    {
        "auditee_name": "Federal awards submitted",
        "post_upload_workbook": {
            "section": FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED,
            "regex": "federal-awards",
        },
    },
    # {
    #     "auditee_name": f"Cert and ETL-{uuid.uuid4()}",
    #     "post_upload_workbooks": [
    #         {
    #             "section": FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED,
    #             "regex": "federal-awards",
    #         },
    #         {
    #             "section": FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE,
    #             "regex": "findings-[0-9]+",
    #         },
    #         {"section": FORM_SECTIONS.FINDINGS_TEXT, "regex": "findings-text"},
    #         {"section": FORM_SECTIONS.CORRECTIVE_ACTION_PLAN, "regex": "captext"},
    #         {"section": FORM_SECTIONS.ADDITIONAL_UEIS, "regex": "additional-ueis"},
    #         {"section": FORM_SECTIONS.SECONDARY_AUDITORS, "regex": "cpas"},
    #         {"section": FORM_SECTIONS.NOTES_TO_SEFA, "regex": "notes"},
    #         {"pdf": "audit/fixtures/basic.pdf"},
    #         {"save": lambda sac: sac.save()},
    #     ],
    # },
]


# MCJ I broke this badly, moving towards E2E with backend data.
# It no longer is a good bootstrap for a single user manually testing.
def _load_single_audit_checklists_for_user(user, workbooks):
    """Create SACs for a given user."""
    logger.info("Creating single audit checklists for %s", user)
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    for submission in SACS:
        auditee_name = submission["auditee_name"]
        sac = SingleAuditChecklist.objects.filter(
            submitted_by=user, general_information__auditee_name=auditee_name
        ).first()
        if sac is None:
            # need to make this object
            sac = _create_sac(user, auditee_name)
        if "post_create_callable" in submission:
            submission["post_create_callable"](sac, user)
        if workbooks and ("post_upload_workbook" in submission):
            # The workbooks directory will contain a list of files.
            # We need to match them based on filename.
            section = submission["post_upload_workbook"]["section"]
            regex = submission["post_upload_workbook"]["regex"]
            # Grab the first filename matching the regex
            file = list(filter(lambda f: re.search(regex, f), workbooks))[0]
            _post_upload_workbook(sac, user, section, file)
        if workbooks and ("post_upload_workbooks" in submission):
            for wb in submission["post_upload_workbooks"]:
                if "section" in wb:
                    section = wb["section"]
                    regex = wb["regex"]
                    workbook_names = list(
                        map(lambda full: (full, Path(full).stem), workbooks)
                    )
                    filtered = list(
                        filter(
                            lambda ftuple: re.search(regex, ftuple[1]), workbook_names
                        )
                    )
                    file = filtered.pop()
                    print("################")
                    print(f"## Loading workbook {file}")
                    print("################")
                    _post_upload_workbook(sac, user, section, file[0])
                if "pdf" in wb:
                    _post_upload_pdf(sac, user, wb["pdf"])
                if "save" in wb:
                    wb["save"](sac)

            sac.save()

            # I couldn't use the transition functions. Don't know why.
            # In progress
            sac.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
            sac.transition_date.append(date.today())

            sac.transition_name.append(SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED)
            sac.transition_date.append(date.today())

            sac.transition_name.append(SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED)
            sac.transition_date.append(date.today())

            sac.transition_name.append(SingleAuditChecklist.STATUS.CERTIFIED)
            sac.transition_date.append(date.today())

            print("CROSS VALIDATING")
            validation_functions = audit.cross_validation.functions

            shape = audit.cross_validation.sac_validation_shape(sac)
            for fun in validation_functions:
                fun(shape)

            sac.validate_cross()

            print("TRANSFERRING DATA... HARDER BETTER FASTER STRONGER ...")
            from audit.etl import ETL

            if sac.general_information:
                etl = ETL(sac)
                etl.load_all()

            sac.transition_name.append(SingleAuditChecklist.STATUS.SUBMITTED)
            sac.transition_date.append(date.today())

    return True


def load_single_audit_checklists():
    """Load example SACs for every user."""

    all_users = User.objects.all()

    for user in all_users:
        _load_single_audit_checklists_for_user(user)


def load_single_audit_checklists_for_email_address(user_email, workbooks):
    """Load example SACs for user with this email address."""

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        logger.info("No user found for %s, have you logged in once?", user_email)
        return

    _load_single_audit_checklists_for_user(user, workbooks)
