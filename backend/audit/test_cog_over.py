from django.test import TestCase
from dissemination.models import CensusGen19, CensusCfda19

from model_bakery import baker
from faker import Faker
from django.db import connection

from .models import SingleAuditChecklist, CognizantBaseline, User

from audit.cog_over import cog_over

# Note:  Fake data is generated for SingleAuditChecklist, CognizantBaseline.
#        Using only the data fields that apply to cog / over assignment.

BASELINE_EIN = "742094204"
BASELINE_DUP_EIN = "987876765"

class CogOverTests(TestCase):
    def __init__(self, method_name: str = "runTest") -> None:
        super().__init__(method_name)

    def setUp(self):
        self.user = baker.make(User)
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(CensusGen19)
            schema_editor.create_model(CensusCfda19)


        gen = baker.make(CensusGen19,
                         index=1, 
                         ein=BASELINE_EIN,
                         dbkey = '102318',
                         totfedexpend = '210000000',
                         )
        gen.save()
        for i in range(6):
            cfda = baker.make(CensusCfda19,
                        index=i, 
                        dbkey = gen.dbkey,
                        cfda = '84.032',
                        amount = 10_000_000 * i,
                        direct = 'Y'
                        )
            cfda.save()
        for i in range(2,5):
            gen = baker.make(CensusGen19,
                         index=i, 
                         ein=BASELINE_DUP_EIN,
                         totfedexpend = '10000000',
                        )
            gen.save()



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
                "total_amount_expended": 52_000_200,
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
    def test_cog_assignment_from_baseline(self):
        sac = baker.make(SingleAuditChecklist,
                        submitted_by=self.user,
                        general_information=self._fake_general(),
                        federal_awards=self._fake_federal_awards(),
                         )
        sac.general_information['ein'] = BASELINE_EIN
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "84")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_no_baseline(self):
        sac = baker.make(SingleAuditChecklist,
                        submitted_by=self.user,
                        general_information=self._fake_general(),
                        federal_awards=self._fake_federal_awards(),
                         )
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_multiple_baseline(self):
        sac = baker.make(SingleAuditChecklist,
                        submitted_by=self.user,
                        general_information=self._fake_general(),
                        federal_awards=self._fake_federal_awards(),
                         )
        sac.general_information['ein'] = BASELINE_DUP_EIN
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_over_assignment(self):
        sac = baker.make(SingleAuditChecklist,
                        submitted_by=self.user,
                        general_information=self._fake_general(),
                        federal_awards=self._fake_federal_awards_lt_cog_limit(),
                        )
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency,None)
        self.assertEqual(over_agency, "15")

    def test_over_assignment_with_baseline(self):
        sac = baker.make(SingleAuditChecklist,
                        submitted_by=self.user,
                        general_information=self._fake_general(),
                        federal_awards=self._fake_federal_awards_lt_cog_limit(),
                        )
        sac.general_information['ein'] = BASELINE_EIN   
        cog_agency, over_agency = cog_over(sac)
        self.assertEqual(cog_agency,None)
        self.assertEqual(over_agency, "15")
"""
TODO

    def test_cog_over_for_gt_cog_limit_gt_da_threshold_factor_cog_2019(self):
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
        )
        # sac.save()
        # self.sac = sac

        # fake_cog_baseline = self._fake_cognizantbaseline()
        # self.cognizantbaseline = CognizantBaseline(
        #     dbkey=fake_cog_baseline["dbkey"],
        #     audit_year=fake_cog_baseline["audit_year"],
        #     ein=self.sac.general_information["ein"],
        #     cognizant_agency=fake_cog_baseline["cognizant_agency"],
        # ).save()
        # cog_agency = None
        # over_agency = None
        cog_agency, over_agency = cog_over(sac)
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
        cog_agency = None
        over_agency = None
        cog_agency, over_agency = cog_over(self.sac)
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)
"""