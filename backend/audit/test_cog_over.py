import json
from pathlib import Path

from django.test import TestCase

from model_bakery import baker
from faker import Faker

from census2019.models import Cfda19, Gen19
from .models import SingleAuditChecklist, CognizantBaseline, User
from dissemination.models import (
    General,
    FederalAward,
)

from audit.cog_over import cog_over


# Note:  Fake data is generated for SingleAuditChecklist, CognizantBaseline.
#        Using only the data fields that apply to cog / over assignment.


class CogOverTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self):
        self.user = baker.make(User)
        sac = SingleAuditChecklist.objects.create(
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
        )
        cognizantbaseline = CognizantBaseline.objects.create(
            self._fake_cognizantbaseline()
        )
        sac.save()
        self.sac = sac
        self.cognizantbaseline = cognizantbaseline


    @staticmethod
    def _fake_general():
        fake = Faker()
        return {
            "ein": fake.ssn().replace("-", ""),
            "audit_type": "single-audit",
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_zip": fake.zipcode(),
            "auditor_ein": fake.ssn().replace("-", ""),
            "auditor_zip": fake.zipcode(),
            "auditee_city": fake.city(),
            "auditee_name": fake.company(),
            "auditor_city": fake.city(),
            "is_usa_based": "true",
            "auditee_email": fake.email(),
            "auditee_phone": fake.basic_phone_number(),
            "auditee_state": fake.state_abbr(),
            "auditor_email": fake.email(),
            "auditor_phone": fake.basic_phone_number(),
            "auditor_state": fake.state_abbr(),
            "auditor_country": "United States",
            "auditor_firm_name": fake.company(),
            "audit_period_covered": "annual",
            "auditee_contact_name": fake.name(),
            "auditor_contact_name": fake.name(),
            "auditee_contact_title": "Boss",
            "auditor_contact_title": "Mega Boss",
            "multiple_eins_covered": "false",
            "multiple_ueis_covered": "false",
            "auditee_address_line_1": fake.street_address(),
            "auditor_address_line_1": fake.street_address(),
            "met_spending_threshold": "true",
            "auditee_fiscal_period_end": "2023-06-01",
            "ein_not_an_ssn_attestation": "true",
            "auditee_fiscal_period_start": "2022-11-01",
            "user_provided_organization_type": "state",
            "auditor_ein_not_an_ssn_attestation": "true",
        }

    @staticmethod
    def _fake_cognizantbaseline():
        fake = Faker()
        return {
            "dbkey": 123456789,
            "audit_year": 2019,
            "ein": fake.ssn().replace("-", ""),
            "cognizant_agency": "20"
        }
    
    @staticmethod
    def _fake_federal_awards():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC123",
                        "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                        "program": {
                            "is_major": "Y",
                            "program_name": "RETIRED AND SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 40_000_000,
                            "audit_report_type": "U",
                            "federal_agency_prefix": "10",
                            "federal_program_total": 45_000_000,
                            "three_digit_extension": "600",
                            "number_of_audit_findings": 0,
                            "additional_award_identification": "COVID-19",
                        },
                        "subrecipients": {"is_passed": "N"},
                        "loan_or_loan_guarantee": {
                            "is_guaranteed": "N",
                            "loan_balance_at_audit_period_end": 0,
                        },
                        "direct_or_indirect_award": {
                            "is_direct": "N",
                            "entities": [
                                {
                                    "passthrough_name": "Bob's Granting House",
                                    "passthrough_identifying_number": "12345",
                                }
                            ],
                        },
                    },
                    {
                        "award_reference": "ABC124",
                        "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                        "program": {
                            "is_major": "Y",
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 11_000_000,
                            "audit_report_type": "U",
                            "federal_agency_prefix": "10",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                            "number_of_audit_findings": 0,
                            "additional_award_identification": "COVID-19",
                        },
                        "subrecipients": {"is_passed": "N"},
                        "loan_or_loan_guarantee": {
                            "is_guaranteed": "N",
                            "loan_balance_at_audit_period_end": 0,
                        },
                        "direct_or_indirect_award": {"is_direct": "Y"},
                    },
                ],
                "total_amount_expended": 51_000_000,
            }
        }


    def test_cog_over(self):
        # Test Case #1 - Cog agency from 2019 with Direct Award > 0.25 * total expended
        # print(
        #     "\n\nTest Case 1 - Cog agency from 2019 with Direct Award > 0.25 * total expended"
        # )
        cog_agency, over_agency = cog_over(self.sac)
        self.assertEqual(over_agency, 0)
