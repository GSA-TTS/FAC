"""Fixtures for SingleAuditChecklist.

We want to create a simple
"""

import json
import logging
from datetime import date, timedelta

from faker import providers

from audit.models import SingleAuditChecklist, Access
from audit.validators import validate_general_information_json
from users.models import User

logger = logging.getLogger(__name__)


def _fake_general_information():
    """Create a fake general_information object."""
    # TODO: can we generate this object from the schema definition in
    # schemas/output/GeneralInformation.schema.json?
    general_information = {
        "auditee_fiscal_period_start": date.today().strftime("%Y-%m-%d"),
        "auditee_fiscal_period_end": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "audit_period_covered": "annual",
        "audit_type": "single-audit",
        "auditee_address_line_1": providers.address.street_address(),
        "auditee_city": providers.address.city(),
        "auditee_contact_name": providers.person.name(),
        "auditee_contact_title": providers.job.job(),
        "auditee_email": providers.internet.ascii_email(),
        "auditee_name": providers.company.company(),
        "auditee_phone": providers.phone_number.phone_number(),
        "auditee_state": providers.address.state(),

    }

    # verify that our created object validates against the schema
    validate_general_information_json(general_information)

    return general_information


def _create_sac(user):
    """Create a single example SAC."""
    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=_fake_general_information(),
    )
    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="editor",
    )
    logger.info("Create single audit checklist %s", sac)


def load_single_audit_checklists():
    """Load example SACs for every user."""

    all_users = User.objects.all()

    for user in all_users:
        logger.info("Creating single audit checklists for %s", user)
        _create_sac(user)
