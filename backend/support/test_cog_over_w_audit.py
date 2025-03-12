from django.contrib.auth import get_user_model
from django.test import TestCase
from dissemination.models import MigrationInspectionRecord

# from audit.models.audit import Audit
from audit.models import (
    Audit,
    SubmissionEvent,
)
from model_bakery import baker
from faker import Faker
from .models.cog_over import CognizantAssignment
from .cog_over_w_audit import compute_cog_over, record_cog_assignment

User = get_user_model()

# Note:  Fake data is generated for Audit.
#        Using only the data fields that apply to cog / over assignment.

UNIQUE_EIN_WITHOUT_DBKEY = "UEWOD1234"
DUP_EIN_WITHOUT_RESOLVER = "DEWOR1234"
EIN_2023_ONLY = "EIN202312"
RESOLVABLE_EIN_WITHOUT_BASELINE = "REWOB1234"
RESOLVABLE_UEI_WITHOUT_BASELINE = "RUWOB1234"
RESOLVABLE_DBKEY_WITHOUT_BASELINE = "20220"
RESOLVABLE_DBKEY_WITH_BASELINE = "202201"
UEI_WITH_BASELINE = "UB0011223"


class CogOverTests(TestCase):
    def __init__(self, method_name: str = "runTest") -> None:
        super().__init__(method_name)

    def setUp(self):
        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000201960",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ei": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2022,
            },
        )

        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=audit.report_id,
            dbkey=None,
            audit_year="2022",
        )
        migration_inspection_record.save()

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-04-CENSUS-0000191850",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                    "auditee_uei": "ZQGGHJH74DW7",
                },
                "audit_year": 2019,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        awards = []
        for i in range(6):
            award = {
                "program": {
                    "federal_agency_prefix": "84",
                    "three_digit_extension": "032",
                    "amount_expended": 10_000_000 * i,
                },
                "direct_or_indirect_award": {"is_direct": "Y"},
            }
            awards.append(award)
        audit.audit["federal_awards"]["awards"] = awards
        audit.save()

        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=audit.report_id,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            audit_year="2019",
        )
        migration_inspection_record.save()

        for i in range(2, 5):
            audit = baker.make(
                Audit,
                version=0,
                report_id=i,
                audit={
                    "federal_awards": {
                        "awards": [],
                        "total_amount_expended": 10000000,
                    },
                    "general_information": {
                        "auditee_ein": DUP_EIN_WITHOUT_RESOLVER,
                        "auditee_uei": "ZQGGHJH74DW7",
                    },
                    "audit_year": 2019,
                },
            )

            migration_inspection_record = baker.make(
                MigrationInspectionRecord,
                report_id=audit.report_id,
                dbkey=str(10_000 + i),
                audit_year="2019",
            )
            migration_inspection_record.save()

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-05-GSAFAC-0000191750",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_ein": RESOLVABLE_EIN_WITHOUT_BASELINE,
                    "auditee_uei": RESOLVABLE_UEI_WITHOUT_BASELINE,
                },
                "audit_year": 2022,
            },
        )

        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=audit.report_id,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            audit_year="2022",
        )
        migration_inspection_record.save()

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-06-CENSUS-0000171851",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_ein": RESOLVABLE_EIN_WITHOUT_BASELINE,
                    "auditee_uei": RESOLVABLE_UEI_WITHOUT_BASELINE,
                },
                "audit_year": 2019,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        awards = []
        for i in range(6):
            award = {
                "program": {
                    "federal_agency_prefix": "22",
                    "three_digit_extension": "032",
                    "amount_expended": 10_000_000 * i,
                },
                "direct_or_indirect_award": {"is_direct": "Y"},
            }
            awards.append(award)
        audit.audit["federal_awards"]["awards"] = awards
        audit.save()

        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=audit.report_id,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            audit_year="2019",
        )
        migration_inspection_record.save()

    @staticmethod
    def _fake_general():
        fake = Faker()
        return {
            "auditee_ein": "ABC123DEF456",
            "audit_type": "single-audit",
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
            "auditee_uei": "FAKEHJH74DW7",
        }

    def _fake_federal_awards(self):
        return {
            "awards": [
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

    def _fake_federal_awards_lt_cog_limit(self):
        return {
            "awards": [
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

    def _fake_federal_awards_lt_da_threshold(self):
        return {
            "awards": [
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

    def _fake_audit(self):
        audit = baker.make(
            Audit,
            version=0,
            report_id="1110-06-GSAFAC-0000171850",
            audit={
                "federal_awards": self._fake_federal_awards(),
                "general_information": self._fake_general(),
                "audit_year": 2023,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_ein"] = audit.auditee_ein = (
            "ABC123DEF456"
        )
        audit.audit["general_information"]["auditee_uei"] = audit.auditee_uei = (
            "ZQGGHJH74DW7"
        )
        audit.save()
        return audit

    def test_cog_assignment_from_hist(self):
        """
        When we have a matching row in 2019 and no cognizant agency,
        we should use the cog computed from 2019 data
        """
        audit = self._fake_audit()
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_ein"] = audit.auditee_ein = (
            UNIQUE_EIN_WITHOUT_DBKEY
        )
        audit.audit["general_information"]["auditee_uei"] = audit.auditee_uei = (
            "ZQGGHJH74DW7"
        )
        audit.audit["federal_awards"]["total_amount_expended"] = 210000000
        audit.save()
        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "84")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_no_hist(self):
        """
        We have no match in 2019. So, assign from 2023"
        """
        audit = self._fake_audit()
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_ein"] = audit.auditee_ein = (
            EIN_2023_ONLY
        )
        audit.save()
        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_multiple_hist(self):
        """
        We have duplicates in 2019. So, assign from 2023
        """

        audit = self._fake_audit()
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_ein"] = audit.auditee_ein = (
            DUP_EIN_WITHOUT_RESOLVER
        )
        audit.save()
        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_hist_resolution(self):
        """
        We have a unique dbkey for the given uei/eint in 2022,
        and we have a match in 2019, but no cognizant agency in 2019 through 2022.
        So, assign from 2019.
        """
        audit = self._fake_audit()
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_ein"] = audit.auditee_ein = (
            RESOLVABLE_EIN_WITHOUT_BASELINE
        )
        audit.audit["general_information"]["auditee_uei"] = audit.auditee_uei = (
            RESOLVABLE_UEI_WITHOUT_BASELINE
        )
        audit.save()
        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "22")
        self.assertEqual(over_agency, None)

    def test_over_assignment(self):
        """
        Awards with totals less than the threshold should result in an oversight agency being assigned.
        """
        audit = baker.make(
            Audit,
            version=0,
            report_id="1110-06-GSAFAC-0000171850",
            audit={
                "federal_awards": self._fake_federal_awards_lt_cog_limit(),
                "general_information": self._fake_general(),
                "audit_year": 2023,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_ein"] = audit.auditee_ein = (
            "ABC123DEF456"
        )
        audit.audit["general_information"]["auditee_uei"] = audit.auditee_uei = (
            "ZQGGHJH74DW7"
        )
        audit.save()
        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, None)
        self.assertEqual(over_agency, "15")

    def test_over_assignment_with_hist(self):
        """
        Awards with totals less than the threshold should result in an oversight agency being assigned.
        And history data should not be used.
        """

        audit = baker.make(
            Audit,
            version=0,
            report_id="1110-06-GSAFAC-0000171850",
            audit={
                "federal_awards": self._fake_federal_awards_lt_cog_limit(),
                "general_information": self._fake_general(),
                "audit_year": 2023,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_ein"] = audit.auditee_ein = (
            UNIQUE_EIN_WITHOUT_DBKEY
        )
        audit.audit["general_information"]["auditee_uei"] = audit.auditee_uei = (
            "ZQGGHJH74DW7"
        )
        audit.save()
        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, None)
        self.assertEqual(over_agency, "15")

    def test_cog_assignment_with_uei_in_baseline(self):
        BASE_UEI = "UEI1"
        BASE_EIN = "EIN1"
        BASE_COG = "00"

        audit = baker.make(
            Audit,
            version=0,
            report_id="1112-07-CENSUS-0000202201",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": BASE_UEI,
                    "auditee_ein": BASE_EIN,
                },
                "audit_year": 2019,
                "cognizant_agency": BASE_COG,
            },
        )
        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-07-CENSUS-0000202201",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 52_000_200,
                },
                "general_information": {
                    "auditee_uei": BASE_UEI,
                    "auditee_ein": BASE_EIN,
                },
                "audit_year": 2022,
            },
        )

        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=audit.report_id,
            dbkey=RESOLVABLE_DBKEY_WITH_BASELINE,
            audit_year="2022",
        )
        migration_inspection_record.save()

        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, BASE_COG)
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_uei_in_baseline_and_override(self):
        BASE_UEI = "UEI1"
        BASE_EIN = "EIN1"
        BASE_COG = "00"

        user = baker.make(
            User,
            email="Test_email",
        )
        audit = baker.make(
            Audit,
            version=0,
            report_id="9991-09-GSAFAC-0000201851",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 52_000_200,
                },
                "general_information": {
                    "auditee_uei": BASE_EIN,
                    "auditee_ein": BASE_UEI,
                },
                "audit_year": 2023,
                "cognizant_agency": BASE_COG,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.event_user = user
        audit.event_type = SubmissionEvent.EventType.SUBMITTED
        audit.save()

        cog_agency, _ = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )

        record_cog_assignment(audit.report_id, audit.event_user, cog_agency)
        cas = CognizantAssignment.objects.all()
        self.assertEqual(len(cas), 1)

        audit = Audit.objects.get(report_id=audit.report_id)
        self.assertEqual(audit.cognizant_agency, cog_agency)

        override_cog = "01"
        CognizantAssignment(
            report_id=audit.report_id,
            cognizant_agency=override_cog,
            assignor_email="test_cog_over   @test.gov",
            override_comment="test_cog_over",
        ).save()
        cas = CognizantAssignment.objects.all()
        self.assertEqual(len(cas), 2)

        audit = Audit.objects.get(report_id=audit.report_id)
        self.assertEqual(audit.cognizant_agency, override_cog)

        audit.event_user = user
        audit.event_type = SubmissionEvent.EventType.SUBMITTED
        audit.audit["cognizant_agency"] = "00"
        audit.save()

        # a re-run ahould create a third assignmenet
        cog_agency, _ = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )

        record_cog_assignment(audit.report_id, audit.event_user, cog_agency)
        audit = Audit.objects.get(report_id=audit.report_id)
        self.assertEqual(audit.cognizant_agency, cog_agency)

    def test_cog_assignment_for_2024_audit(self):

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202460",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2024,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_fiscal_period_end"] = "2024-05-31"
        audit.audit["general_information"]["auditee_fiscal_period_start"] = "2023-06-01"
        awards = []
        for i in range(6):
            award = {
                "program": {
                    "federal_agency_prefix": "84",
                    "three_digit_extension": "032",
                    "amount_expended": 10_000_000 * i,
                },
                "direct_or_indirect_award": {"is_direct": "Y"},
            }
            awards.append(award)
        audit.audit["federal_awards"]["awards"] = awards
        audit.save()

        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "84")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_w_baseline(self):
        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202760",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2027,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_fiscal_period_end"] = "2027-05-31"
        audit.audit["general_information"]["auditee_fiscal_period_start"] = "2026-06-01"
        audit.save()

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202460",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2024,
                "cognizant_agency": "24",
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        awards = []
        for i in range(6):
            award = {
                "program": {
                    "federal_agency_prefix": "14",
                    "three_digit_extension": "032",
                    "amount_expended": 10_000_000 * i,
                },
                "direct_or_indirect_award": {"is_direct": "Y"},
            }
            awards.append(award)
        audit.audit["federal_awards"]["awards"] = awards
        audit.save()

        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "24")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_no_baseline(self):
        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202761",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW8",
                    "auditee_ein": "EI27NOBAS",
                },
                "audit_year": 2027,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_fiscal_period_end"] = "2027-05-31"
        audit.audit["general_information"]["auditee_fiscal_period_start"] = "2026-06-01"
        awards = []
        for i in range(6):
            award = {
                "program": {
                    "federal_agency_prefix": "10",
                    "three_digit_extension": "032",
                    "amount_expended": 10_000_000 * i,
                },
                "direct_or_indirect_award": {"is_direct": "Y"},
            }
            awards.append(award)
        audit.audit["federal_awards"]["awards"] = awards
        audit.save()

        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_w_base_to_2026_cog(self):
        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202760",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2027,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_fiscal_period_end"] = "2027-05-31"
        audit.audit["general_information"]["auditee_fiscal_period_start"] = "2026-06-01"
        audit.save()

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202460",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2024,
                "cognizant_agency": "24",
            },
        )

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202560",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 200000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2025,
                "cognizant_agency": "14",
            },
        )

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202660",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 200000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2026,
                "cognizant_agency": "04",
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        awards = []
        for i in range(6):
            award = {
                "program": {
                    "federal_agency_prefix": "14",
                    "three_digit_extension": "032",
                    "amount_expended": 10_000_000 * i,
                },
                "direct_or_indirect_award": {"is_direct": "Y"},
            }
            awards.append(award)
        audit.audit["federal_awards"]["awards"] = awards
        audit.save()

        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "04")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_no_base_to_2026(self):
        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202060",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2020,
                "cognizant_agency": "34",
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        awards = []
        for i in range(6):
            award = {
                "program": {
                    "federal_agency_prefix": "14",
                    "three_digit_extension": "032",
                    "amount_expended": 10_000_000 * i,
                },
                "direct_or_indirect_award": {"is_direct": "Y"},
            }
            awards.append(award)
        audit.audit["federal_awards"]["awards"] = awards
        audit.save()

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202660",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 200000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2026,
                "cognizant_agency": "10",
            },
        )

        audit = baker.make(
            Audit,
            version=0,
            report_id="1111-03-GSAFAC-0000202760",
            audit={
                "federal_awards": {
                    "awards": [],
                    "total_amount_expended": 210000000,
                },
                "general_information": {
                    "auditee_uei": "ZQGGHJH74DW7",
                    "auditee_ein": UNIQUE_EIN_WITHOUT_DBKEY,
                },
                "audit_year": 2027,
            },
        )
        audit = Audit.objects.get(report_id=audit.report_id)
        audit.audit["general_information"]["auditee_fiscal_period_end"] = "2027-05-31"
        audit.audit["general_information"]["auditee_fiscal_period_start"] = "2026-06-01"
        audit.save()

        cog_agency, over_agency = compute_cog_over(
            audit.audit["federal_awards"],
            audit.submission_status,
            audit.auditee_ein,
            audit.auditee_uei,
            audit.audit_year,
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)
