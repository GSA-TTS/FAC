"""Fixtures for Audit.

We want to create a variety of Audits in different states of
completion.
"""

import logging
from datetime import date, timedelta

from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from faker import Faker

from audit import intakelib
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
        "auditor_country": "USA",
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
        "secondary_auditors_exist": False,
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
    data_step_2 = {
        "auditor_name": fake.name(),
        "auditor_title": fake.job(),
        "auditor_certification_date_signed": fake.date(),
    }

    return data_step_1, data_step_2


def fake_auditee_certification():
    """Create fake auditee confirmation form data."""
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


def _create_audit(user, auditee_name, submission_status="in_progress"):
    """Create a single example Audit."""
    Audit = apps.get_model("audit.Audit")
    audit = Audit.objects.create(
        audit={"general_information": _fake_general_information(auditee_name)},
        submission_status=submission_status,
        event_user=user,
        event_type="created",
    )

    Access = apps.get_model("audit.Access")
    Access.objects.create(
        audit=audit,
        user=user,
        email=user.email,
        role="editor",
    )
    Access.objects.create(
        audit=audit,
        user=user,
        email=user.email,
        role="certifying_auditor_contact",
    )
    Access.objects.create(
        audit=audit,
        user=user,
        email=user.email,
        role="certifying_auditee_contact",
    )
    logger.info("Created audit %s", audit)
    return audit


def _post_create_federal_awards(this_audit, this_user):
    """Upload a federal awards workbook for this Audit.

    This should be idempotent if it is called on a Audit that already
    has a federal awards file uploaded.
    """
    ExcelFile = apps.get_model("audit.ExcelFile")

    if (
        ExcelFile.objects.filter(
            audit_id=this_audit.id, form_section=FORM_SECTIONS.FEDERAL_AWARDS
        ).exists()
        and this_audit.audit.get("federal_awards") is not None
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
        audit_id=this_audit.id,
        form_section=FORM_SECTIONS.FEDERAL_AWARDS,
    )
    excel_file.full_clean()
    excel_file.save()
    # TODO: refactor the upload handling from the post view into a
    # function so we can call it here instead of aping it.
    audit_data = intakelib.extract_federal_awards(excel_file.file)
    audit.validators.validate_federal_award_json(audit_data)
    this_audit.audit.update({"federal_awards": audit_data})
    this_audit.save()

    logger.info("Created Federal Awards workbook upload for Audit %s", this_audit.id)


# list of the default SingleAuditChecklists to create for each user
# The auditee name is used to disambiguate them, so it must be unique
# or another Audit won't be created.
# If `post_create_callable` exists for an item, it should be a
# callable(audit, user) that does further processing after the Audit
# is created.
AUDITS = [
    {"auditee_name": "Audit in progress"},
    {
        "auditee_name": "Audit ready for certification",
        "submission_status": "ready_for_certification",
    },
    {"auditee_name": "Audit fully submitted", "submission_status": "disseminated"},
]


def _load_audits_for_user(user):
    """Create Audits for a given user."""
    logger.info("Creating audit for %s", user)
    Audit = apps.get_model("audit.Audit")
    for item_info in AUDITS:
        auditee_name = item_info["auditee_name"]
        submission_status = item_info.get("submission_status", "in_progress")
        audit = Audit.objects.filter(created_by=user, auditee_name=auditee_name).first()
        if audit is None:
            # need to make this object
            audit = _create_audit(user, auditee_name, submission_status)


def load_audits():
    """Load example Audits for every user."""

    all_users = User.objects.all()

    for user in all_users:
        _load_audits_for_user(user)


def load_audits_for_email_address(user_email, workbooks=None):
    """Load example Audits for user with this email address."""
    # Unfinished code for handling specific workbooks was checked into the
    # load_fixtures command; this handles the additional argument so that in
    # future that work can be wired in.
    if workbooks is None:
        workbooks = []

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        logger.info("No user found for %s, have you logged in once?", user_email)
        return

    _load_audits_for_user(user)
