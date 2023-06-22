"""Fixtures for SingleAuditChecklist.

We want to create a simple
"""

import logging
from datetime import date, timedelta

from django.apps import apps

from faker import Faker

import audit.validators
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


# list of the default SingleAuditChecklists to create for each user
# The auditee name is used to disambiguate them
SACS = [
    {"auditee_name": "SAC in progress", "submission_status": "in_progress"},
]


def load_single_audit_checklists():
    """Load example SACs for every user."""

    all_users = User.objects.all()
    SingleAuditChecklist = apps.get_model("audit.SingleAuditChecklist")

    for user in all_users:
        logger.info("Creating single audit checklists for %s", user)
        for item_info in SACS:
            auditee_name = item_info["auditee_name"]
            if not SingleAuditChecklist.objects.filter(
                submitted_by=user, general_information__auditee_name=auditee_name
            ).exists():
                # need to make this object
                _create_sac(user, auditee_name)
