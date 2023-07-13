"""Fixtures for SingleAuditChecklist.
We want to create a simple
"""

import logging
from datetime import date, timedelta
from random import SystemRandom

from faker import Faker

from ..models import Access, SingleAuditChecklist

logger = logging.getLogger(__name__)


def _fake_general_information():
    """Create a fake general_information object."""
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
        "auditee_name": fake.company(),
        "auditee_phone": fake.basic_phone_number(),
        "auditee_state": fake.state_abbr(include_territories=False),
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
        "auditor_state": fake.state_abbr(include_territories=False),
        "auditor_zip": fake.postalcode(),
        "ein": fake.ssn().replace("-", ""),
        "ein_not_an_ssn_attestation": True,
        "is_usa_based": True,
        "met_spending_threshold": True,
        "multiple_eins_covered": False,
        "multiple_ueis_covered": False,
        "user_provided_organization_type": "unknown",
    }
    return general_information


def _fake_federal_awards():
    federal_awards = {
        "FederalAwards": {
            "auditee_uei": "ABC123DEF456",
            "federal_awards": [
                {
                    "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                    "program": {
                        "is_major": "Y",
                        "program_name": "RETIRED AND SENIOR VOLUNTEER PROGRAM",
                        "amount_expended": 9000,
                        "audit_report_type": "U",
                        "federal_agency_prefix": "93",
                        "federal_program_total": 9000,
                        "three_digit_extension": "600",
                        "number_of_audit_findings": 0,
                        "additional_award_identification": "COVID-19",
                    },
                    "subrecipients": {"is_passed": "N"},
                    "loan_or_loan_guarantee": {"is_guaranteed": "N"},
                    "direct_or_indirect_award": {"is_direct": "Y"},
                }
            ],
            "total_amount_expended": 9000,
        }
    }
    return federal_awards


def _fake_additional_auditors():
    fake = Faker()
    additional_auditors = {
        "AdditionalAuditors": {
            "auditors": [
                {
                    "auditor_seq_number": i,
                    "auditor_address_line_1": fake.street_address(),
                    "auditor_city": fake.city(),
                    "auditor_contact_name": fake.name(),
                    "auditor_contact_title": fake.job(),
                    "auditor_country": fake.country(),
                    "auditor_ein": fake.ssn().replace("-", ""),
                    "auditor_email": fake.ascii_email(),
                    "auditor_firm_name": fake.company(),
                    "auditor_phone": fake.basic_phone_number(),
                    "auditor_state": fake.state_abbr(include_territories=False),
                    "auditor_zip": fake.postalcode(),
                }
                for i in range(SystemRandom().randrange(1, 4))
            ]
        }
    }
    return additional_auditors


def _create_sac(user):
    """Create a single example SAC."""
    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        general_information=_fake_general_information(),
        additional_auditors=_fake_additional_auditors(),
        federal_awards=_fake_federal_awards(),
    )

    Access.objects.create(
        sac=sac,
        user=user,
        email=user.email,
        role="editor",
    )
    logger.info("Created single audit checklist %s", sac)
    return sac


def load_single_audit_checklists_for_user(user):
    """Create SACs for a given user."""
    logger.info("Creating single audit checklists for %s", user)
    return _create_sac(user)
