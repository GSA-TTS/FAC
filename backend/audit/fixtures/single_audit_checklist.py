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

from audit.excel import (
    extract_federal_awards,
    extract_findings_uniform_guidance,
    extract_findings_text
)
import audit.validators

from audit.fixtures.excel import FORM_SECTIONS
from users.models import User

logger = logging.getLogger(__name__)


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


def _create_sac(user, auditee_name):
    """Create a single example SAC."""
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=_fake_general_information(auditee_name),
    )

    Access = apps.get_model("audit.Access")
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="editor",
    )
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


extract_mapping = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED : extract_federal_awards,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE : extract_findings_uniform_guidance,
    FORM_SECTIONS.FINDINGS_TEXT : extract_findings_text
}

validator_mapping = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED : audit.validators.validate_federal_award_json,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE : audit.validators.validate_findings_uniform_guidance_json,
    FORM_SECTIONS.FINDINGS_TEXT : audit.validators.validate_findings_text_json
}

def _post_upload_workbook(this_sac, this_user, section, xlsx_filename):
    """Upload a workbook for this SAC.

    This should be idempotent if it is called on a SAC that already
    has a federal awards file uploaded.
    """
    ExcelFile = apps.get_model("audit.ExcelFile")

    if (
        ExcelFile.objects.filter(
            sac_id=this_sac.id, form_section=section
        ).exists()
        and this_sac.federal_awards is not None
    ):
        # there is already an uploaded file and data in the object so
        # nothing to do here
        return

    with open(xlsx_filename, "rb") as f:
        content = f.read()
    file = SimpleUploadedFile(xlsx_filename, content, "application/vnd.ms-excel")
    excel_file = ExcelFile(
        file=file,
        filename=Path(xlsx_filename).stem,
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

    this_sac.save()

    logger.info("Created Federal Awards workbook upload for SAC %s", this_sac.id)
    
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
            "regex": "federal-awards"
        }
    },
    {
        "auditee_name": "All workbooks submitted",
        "post_upload_workbooks": [
            {
            "section": FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED,
            "regex": "federal-awards"
            },
            {
            "section": FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE,
            "regex": "findings-[0-9]+"
            },
            {
            "section": FORM_SECTIONS.FINDINGS_TEXT,
            "regex": "findings-text"
            },
        ]
    },
]


def _load_single_audit_checklists_for_user(user, workbooks):
    """Create SACs for a given user."""
    logger.info("Creating single audit checklists for %s", user)
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")
    for item_info in SACS:
        auditee_name = item_info["auditee_name"]
        sac = SingleAuditChecklist.objects.filter(
            submitted_by=user, general_information__auditee_name=auditee_name
        ).first()
        if sac is None:
            # need to make this object
            sac = _create_sac(user, auditee_name)
        if "post_create_callable" in item_info:
            item_info["post_create_callable"](sac, user)
        if workbooks and ("post_upload_workbook" in item_info):
            # The workbooks directory will contain a list of files.
            # We need to match them based on filename. 
            section = item_info["post_upload_workbook"]["section"]
            regex = item_info["post_upload_workbook"]["regex"]
            # Grab the first filename matching the regex
            file = list(filter(lambda f: re.search(regex, f), workbooks))[0]
            _post_upload_workbook(sac, user, section, file)
        if workbooks and ("post_upload_workbooks" in item_info):
            for wb in item_info["post_upload_workbooks"]:
                section = wb["section"]
                regex = wb["regex"]
                print(f"{section} Looking for {regex} in {workbooks}")
                workbook_names = list(map(lambda full: (full, Path(full).stem), workbooks))
                print(workbook_names)
                filtered = list(filter(lambda ftuple: re.search(regex, ftuple[1]), workbook_names))
                print(filtered)
                file = filtered.pop()
                print("################")
                print(f"## Loading workbook {file}")
                print("################")
                _post_upload_workbook(sac, user, section, file[0])



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
