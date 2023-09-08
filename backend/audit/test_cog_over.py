from django.test import TestCase

from model_bakery import baker
from faker import Faker

from .models import SingleAuditChecklist, CognizantBaseline, User
from dissemination.models import CensusGen22, cognizant_agencies_2021_2025

from audit.cog_over import cog_over

# Note:  Fake data is generated for SingleAuditChecklist, CognizantBaseline.
#        Using only the data fields that apply to cog / over assignment.


class CogOverTests(TestCase):
    def __init__(self, method_name: str = "runTest") -> None:
        super().__init__(method_name)

    def setUp(self):
        self.user = baker.make(User)

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
            "auditor_country": "non-USA",
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
            "cognizant_agency": "20",
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

    @staticmethod
    def _fake_federal_awards_lt_cog_limit():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC125",
                        "program": {
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 11_000_000,
                            "federal_agency_prefix": "15",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                        },
                        "direct_or_indirect_award": {"is_direct": "Y"},
                    },
                ],
                "total_amount_expended": 11_000_000,
            }
        }

    @staticmethod
    def _fake_federal_awards_lt_da_threshold():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC125",
                        "program": {
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 11_000_000,
                            "federal_agency_prefix": "25",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                        },
                        "direct_or_indirect_award": {"is_direct": "Y"},
                    },
                ],
                "total_amount_expended": 49_000_000,
            }
        }

    @staticmethod
    def _fake_CensusGen22_1():
        fake = Faker()
        return {
            "audityear": 2022,
            "dbkey": 20576,
            "ein": fake.ssn().replace("-", ""),
            "uei": "ZQGGHJH74DW7",
        }

    @staticmethod
    def _fake_CensusGen22_2():
        fake = Faker()
        return {
            "audityear": 2022,
            "dbkey": 20577,
            "ein": fake.ssn().replace("-", ""),
            "uei": "ZQGGHJH74DW8",
        }

    @staticmethod
    def _fake_CensusGen22_3():
        fake = Faker()
        return {
            "audityear": 2022,
            "dbkey": 20578,
            "ein": fake.ssn().replace("-", ""),
            "uei": "ZQGGHJH74DW9",
        }

    @staticmethod
    def _fake_CensusGen22_4():
        fake = Faker()
        return {
            "audityear": 2022,
            "dbkey": 20579,
            "ein": fake.ssn().replace("-", ""),
            "uei": "ZQGGHJH74DW6",
        }

    @staticmethod
    def _fake_cognizant_agencies_2021_2025_1():
        fake = Faker()
        return {
            "ein": fake.ssn().replace("-", ""),
            "dbkey": 20576,
            "cogagency": 87,
        }

    @staticmethod
    def _fake_cognizant_agencies_2021_2025_2():
        fake = Faker()
        return {
            "ein": fake.ssn().replace("-", ""),
            "dbkey": 20577,
            "cogagency": 88,
        }

    @staticmethod
    def _fake_cognizant_agencies_2021_2025_3():
        fake = Faker()
        return {
            "ein": fake.ssn().replace("-", ""),
            "dbkey": 20578,
            "cogagency": 89,
        }

    @staticmethod
    def _fake_cognizant_agencies_2021_2025_4():
        fake = Faker()
        return {
            "ein": fake.ssn().replace("-", ""),
            "dbkey": 20579,
            "cogagency": 90,
        }

    def test_cog_over_for_gt_cog_limit_gt_da_threshold_factor_cog_2019(self):
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
        )
        sac.save()
        self.sac = sac

        fake_cog_baseline = self._fake_cognizantbaseline()
        self.cognizantbaseline = CognizantBaseline(
            dbkey=fake_cog_baseline["dbkey"],
            audit_year=fake_cog_baseline["audit_year"],
            ein=self.sac.general_information["ein"],
            cognizant_agency=fake_cog_baseline["cognizant_agency"],
        ).save()

        fake_CensusGen22 = self._fake_CensusGen22_1()
        self.CensusGen22 = CensusGen22.objects.create(
            dbkey=fake_CensusGen22["dbkey"],
            ein=fake_CensusGen22["ein"],
            uei=fake_CensusGen22["uei"],
        ).save()

        fake_cognizant_agencies_2021_2025 = self._fake_cognizant_agencies_2021_2025_1()
        self.cognizant_agencies_2021_2025 = cognizant_agencies_2021_2025.objects.create(
            dbkey=fake_cognizant_agencies_2021_2025["dbkey"],
            ein=fake_cognizant_agencies_2021_2025["ein"],
            cogagency=fake_cognizant_agencies_2021_2025["cogagency"],
        ).save()

        cog_agency = None
        over_agency = None
        cog_agency, over_agency = cog_over(self.sac)
        self.assertEqual(cog_agency, "20")
        self.assertEqual(over_agency, None)

    def test_cog_over_for_lt_cog_lit_gt_da_threshold_factor_oversight(self):
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards_lt_cog_limit(),
        )
        sac.save()
        self.sac = sac

        fake_cog_baseline = self._fake_cognizantbaseline()
        self.cognizantbaseline = CognizantBaseline(
            dbkey=fake_cog_baseline["dbkey"],
            audit_year=fake_cog_baseline["audit_year"],
            ein=self.sac.general_information["ein"],
            cognizant_agency=fake_cog_baseline["cognizant_agency"],
        ).save()

        fake_CensusGen22 = self._fake_CensusGen22_2()
        self.CensusGen22 = CensusGen22.objects.create(
            dbkey=fake_CensusGen22["dbkey"],
            ein=fake_CensusGen22["ein"],
            uei=fake_CensusGen22["uei"],
        ).save()

        fake_cognizant_agencies_2021_2025 = self._fake_cognizant_agencies_2021_2025_2()
        self.cognizant_agencies_2021_2025 = cognizant_agencies_2021_2025.objects.create(
            dbkey=fake_cognizant_agencies_2021_2025["dbkey"],
            ein=fake_cognizant_agencies_2021_2025["ein"],
            cogagency=fake_cognizant_agencies_2021_2025["cogagency"],
        ).save()

        cog_agency = None
        over_agency = None
        cog_agency, over_agency = cog_over(self.sac)
        self.assertEqual(cog_agency, None)
        self.assertEqual(over_agency, "15")

    def test_cog_over_for_lt_cog_limit_lt_da_threshold_oversight(self):
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards_lt_da_threshold(),
        )
        sac.save()
        self.sac = sac

        fake_cog_baseline = self._fake_cognizantbaseline()
        self.cognizantbaseline = CognizantBaseline(
            dbkey=fake_cog_baseline["dbkey"],
            audit_year=fake_cog_baseline["audit_year"],
            ein=self.sac.general_information["ein"],
            cognizant_agency=fake_cog_baseline["cognizant_agency"],
        ).save()

        fake_CensusGen22 = self._fake_CensusGen22_3()
        self.CensusGen22 = CensusGen22.objects.create(
            dbkey=fake_CensusGen22["dbkey"],
            ein=fake_CensusGen22["ein"],
            uei=fake_CensusGen22["uei"],
        ).save()

        fake_cognizant_agencies_2021_2025 = self._fake_cognizant_agencies_2021_2025_3()
        self.cognizant_agencies_2021_2025 = cognizant_agencies_2021_2025.objects.create(
            dbkey=fake_cognizant_agencies_2021_2025["dbkey"],
            ein=fake_cognizant_agencies_2021_2025["ein"],
            cogagency=fake_cognizant_agencies_2021_2025["cogagency"],
        ).save()

        cog_agency = None
        over_agency = None
        cog_agency, over_agency = cog_over(self.sac)
        self.assertEqual(cog_agency, None)
        self.assertEqual(over_agency, "25")

    def test_cog_over_gt_cog_limit_no_2019(self):
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
        )
        sac.save()
        self.sac = sac

        fake_cog_baseline = self._fake_cognizantbaseline()
        self.cognizantbaseline = CognizantBaseline(
            dbkey=fake_cog_baseline["dbkey"],
            audit_year=fake_cog_baseline["audit_year"],
            ein=fake_cog_baseline["ein"],
            cognizant_agency=fake_cog_baseline["cognizant_agency"],
        ).save()

        fake_CensusGen22 = self._fake_CensusGen22_4()
        self.CensusGen22 = CensusGen22.objects.create(
            dbkey=fake_CensusGen22["dbkey"],
            ein=fake_CensusGen22["ein"],
            uei=fake_CensusGen22["uei"],
        ).save()

        fake_cognizant_agencies_2021_2025 = self._fake_cognizant_agencies_2021_2025_4()
        self.cognizant_agencies_2021_2025 = cognizant_agencies_2021_2025.objects.create(
            dbkey=fake_cognizant_agencies_2021_2025["dbkey"],
            ein=fake_cognizant_agencies_2021_2025["ein"],
            cogagency=fake_cognizant_agencies_2021_2025["cogagency"],
        ).save()

        cog_agency = None
        over_agency = None
        cog_agency, over_agency = cog_over(self.sac)
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)
