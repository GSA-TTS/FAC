from django.test import TestCase
from dissemination.hist_models.census_2019 import CensusGen19, CensusCfda19
from dissemination.hist_models.census_2022 import CensusGen22

from model_bakery import baker
from faker import Faker
from django.db import connection

from audit.models import SingleAuditChecklist
from .models import CognizantBaseline

from .cog_over import cog_over

# Note:  Fake data is generated for SingleAuditChecklist, CognizantBaseline.
#        Using only the data fields that apply to cog / over assignment.

UNIQUE_EIN_WITHOUT_DBKEY = "UEWOD1234"
DUP_EIN_WITHOUT_RESOLVER = "DEWOR1234"
EIN_2023_ONLY = "EIN202312"
RESOLVABLE_EIN_WITHOUT_BASELINE = "REWOB1234"
RESOLVABLE_UEI_WITHOUT_BASELINE = "RUWOB1234"
RESOLVABLE_DBKEY_WITHOUT_BASELINE = "20220"
UEI_WITH_BASELINE = "UB0011223"


class CogOverTests(TestCase):
    def __init__(self, method_name: str = "runTest") -> None:
        super().__init__(method_name)

    def setUp(self):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(CensusGen19)
            schema_editor.create_model(CensusGen22)
            schema_editor.create_model(CensusCfda19)

        gen = baker.make(
            CensusGen19,
            index=1,
            ein=UNIQUE_EIN_WITHOUT_DBKEY,
            dbkey=None,
            totfedexpend="210000000",
        )
        gen.save()
        for i in range(6):
            cfda = baker.make(
                CensusCfda19,
                index=i,
                ein=gen.ein,
                dbkey=gen.dbkey,
                cfda="84.032",
                amount=10_000_000 * i,
                direct="Y",
            )
            cfda.save()
        for i in range(2, 5):
            gen = baker.make(
                CensusGen19,
                index=i,
                ein=DUP_EIN_WITHOUT_RESOLVER,
                dbkey=str(10_000 + i),
                totfedexpend="10000000",
            )
            gen.save()
        gen = baker.make(
            CensusGen22,
            index=11,
            ein=RESOLVABLE_EIN_WITHOUT_BASELINE,
            uei=RESOLVABLE_UEI_WITHOUT_BASELINE,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            totfedexpend="210000000",
        )
        gen.save()
        gen = baker.make(
            CensusGen19,
            index=11,
            ein=RESOLVABLE_EIN_WITHOUT_BASELINE,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            totfedexpend="210000000",
        )
        gen.save()
        for i in range(6):
            cfda = baker.make(
                CensusCfda19,
                index=i + 10,
                ein=gen.ein,
                dbkey=gen.dbkey,
                cfda="22.032",
                amount=10_000_000 * i,
                direct="Y",
            )
            cfda.save()

    @staticmethod
    def _fake_general():
        fake = Faker()
        return {
            "ein": "ABC123DEF456",
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
            "cognizant_agency": "20",
        }

    def _fake_federal_awards(self):
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
                "total_amount_expended": 52_000_200,
            }
        }

    def _fake_federal_awards_lt_cog_limit(self):
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC125",
                        "program": {
                            "program_name": "SENIOR VOLUNTEER PROGRAM",
                            "amount_expended": 11_200_300,
                            "federal_agency_prefix": "15",
                            "federal_program_total": 12_000_000,
                            "three_digit_extension": "600",
                        },
                        "direct_or_indirect_award": {"is_direct": "Y"},
                    },
                ],
                "total_amount_expended": 11_200_300,
            }
        }

    def _fake_federal_awards_lt_da_threshold(self):
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

    def _fake_sac(self):
        sac = baker.make(
            SingleAuditChecklist,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
        )
        return sac

    def test_cog_assignment_from_hist(self):
        """
        When we have a matching row in 2019 and nothing in the
        baseline table, we should use the cog computed from 2019 data
        """
        sac = self._fake_sac()
        sac.general_information["ein"] = UNIQUE_EIN_WITHOUT_DBKEY
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "84")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_no_hist(self):
        """
        We have no match in the base sheet and we
        have no match in 2019. So, assign from 2023"
        """
        sac = self._fake_sac()
        sac.general_information["ein"] = EIN_2023_ONLY
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_multiple_hist(self):
        """
        We have no match in the base sheet and we
        have duplicates in 2019. So, assign from 2023
        """

        sac = self._fake_sac()
        sac.general_information["ein"] = DUP_EIN_WITHOUT_RESOLVER
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_hist_resolution(self):
        """
        We have a unique dbkey for the given uei/eint in 2022,
        and we have a match in 2019, but nothing in the baseline.
        So, assign from 2019
        """
        sac = self._fake_sac()

        sac.general_information["ein"] = RESOLVABLE_EIN_WITHOUT_BASELINE
        sac.general_information["auditee_uei"] = RESOLVABLE_UEI_WITHOUT_BASELINE
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "22")
        self.assertEqual(over_agency, None)

    def test_over_assignment(self):
        """
        Awards with totals less than the threshold should result in an oversight agency being assigned.
        """
        sac = baker.make(
            SingleAuditChecklist,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards_lt_cog_limit(),
        )
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, None)
        self.assertEqual(over_agency, "15")

    def test_over_assignment_with_hist(self):
        """
        Awards with totals less than the threshold should result in an oversight agency being assigned.
        And history data should not be used.
        """
        sac = baker.make(
            SingleAuditChecklist,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards_lt_cog_limit(),
        )
        sac.general_information["ein"] = UNIQUE_EIN_WITHOUT_DBKEY
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, None)
        self.assertEqual(over_agency, "15")

    def test_cog_assignment_with_uei_in_baseline(self):
        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = UEI_WITH_BASELINE
        baker.make(
            CognizantBaseline,
            uei=UEI_WITH_BASELINE,
            cognizant_agency="17",
        )
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "17")
        self.assertEqual(over_agency, None)
