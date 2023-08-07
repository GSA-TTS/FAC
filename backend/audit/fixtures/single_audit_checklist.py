"""Fixtures for SingleAuditChecklist.

We want to create a variety of SACs in different states of
completion.
"""

import logging
from datetime import date, timedelta

from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker

import audit.excel
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
    data_step_2 = {"auditor_name": fake.name(), "auditor_title": fake.job()}

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
    data_step_2 = {"auditee_name": fake.name(), "auditee_title": fake.job()}

    return data_step_1, data_step_2


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
        "post_create_callable": _post_create_federal_awards,
    },
]


def _load_single_audit_checklists_for_user(user):
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


def load_single_audit_checklists():
    """Load example SACs for every user."""

    all_users = User.objects.all()

    for user in all_users:
        _load_single_audit_checklists_for_user(user)


def load_single_audit_checklists_for_email_address(user_email):
    """Load example SACs for user with this email address."""

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        logger.info("No user found for %s, have you logged in once?", user_email)
        return

    _load_single_audit_checklists_for_user(user)
