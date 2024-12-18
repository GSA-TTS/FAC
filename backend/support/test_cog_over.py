from django.test import TestCase
from dissemination.models import General, MigrationInspectionRecord, FederalAward

from model_bakery import baker
from faker import Faker

from audit.models import SingleAuditChecklist
from .models import CognizantAssignment

from .cog_over import compute_cog_over, record_cog_assignment

# Note:  Fake data is generated for SingleAuditChecklist.
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
        gen = baker.make(
            General,
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            report_id="1111-03-GSAFAC-0000201960",
            total_amount_expended="210000000",
            audit_year="2022",
        )
        gen.save()
        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=gen.report_id,
            dbkey=None,
            audit_year="2022",
        )
        migration_inspection_record.save()
        gen = baker.make(
            General,
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            report_id="1111-04-CENSUS-0000191850",
            total_amount_expended="210000000",
            audit_year="2019",
        )
        gen.save()
        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=gen.report_id,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            audit_year="2019",
        )
        migration_inspection_record.save()
        for i in range(6):
            cfda = baker.make(
                FederalAward,
                report_id=gen,
                federal_agency_prefix="84",
                federal_award_extension="032",
                amount_expended=10_000_000 * i,
                is_direct="Y",
            )
            cfda.save()
        for i in range(2, 5):
            gen = baker.make(
                General,
                auditee_ein=DUP_EIN_WITHOUT_RESOLVER,
                report_id=i,
                total_amount_expended="10000000",
                audit_year="2019",
            )
            gen.save()
            migration_inspection_record = baker.make(
                MigrationInspectionRecord,
                report_id=gen.report_id,
                dbkey=str(10_000 + i),
                audit_year="2019",
            )
            migration_inspection_record.save()

        gen = baker.make(
            General,
            report_id="1111-05-GSAFAC-0000191750",
            auditee_ein=RESOLVABLE_EIN_WITHOUT_BASELINE,
            auditee_uei=RESOLVABLE_UEI_WITHOUT_BASELINE,
            total_amount_expended="210000000",
            audit_year="2022",
        )
        gen.save()
        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=gen.report_id,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            audit_year="2022",
        )
        migration_inspection_record.save()

        gen = baker.make(
            General,
            auditee_ein=RESOLVABLE_EIN_WITHOUT_BASELINE,
            auditee_uei=RESOLVABLE_UEI_WITHOUT_BASELINE,
            report_id="1111-06-CENSUS-0000171851",
            total_amount_expended="210000000",
            audit_year="2019",
        )
        gen.save()
        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=gen.report_id,
            dbkey=RESOLVABLE_DBKEY_WITHOUT_BASELINE,
            audit_year="2019",
        )
        migration_inspection_record.save()
        for i in range(6):
            cfda = baker.make(
                FederalAward,
                report_id=gen,
                federal_agency_prefix="22",
                federal_award_extension="032",
                amount_expended=10_000_000 * i,
                is_direct="Y",
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
            "audit_year": "2023",
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
        When we have a matching row in 2019 and no cognizant agency,
        we should use the cog computed from 2019 data
        """
        sac = self._fake_sac()
        sac.general_information["ein"] = UNIQUE_EIN_WITHOUT_DBKEY
        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "84")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_no_hist(self):
        """
        We have no match in 2019. So, assign from 2023"
        """
        sac = self._fake_sac()
        sac.general_information["ein"] = EIN_2023_ONLY
        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_multiple_hist(self):
        """
        We have duplicates in 2019. So, assign from 2023
        """

        sac = self._fake_sac()
        sac.general_information["ein"] = DUP_EIN_WITHOUT_RESOLVER
        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_hist_resolution(self):
        """
        We have a unique dbkey for the given uei/eint in 2022,
        and we have a match in 2019, but no cognizant agency in 2019 through 2022.
        So, assign from 2019.
        """
        sac = self._fake_sac()

        sac.general_information["ein"] = RESOLVABLE_EIN_WITHOUT_BASELINE
        sac.general_information["auditee_uei"] = RESOLVABLE_UEI_WITHOUT_BASELINE
        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
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
        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
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
        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, None)
        self.assertEqual(over_agency, "15")

    def test_cog_assignment_with_uei_in_baseline(self):
        BASE_UEI = "UEI1"
        BASE_EIN = "EIN1"
        BASE_COG = "00"

        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = BASE_UEI
        sac.general_information["ein"] = BASE_EIN

        gen = baker.make(
            General,
            report_id="1111-07-CENSUS-0000161749",
            auditee_ein=BASE_EIN,
            auditee_uei=BASE_UEI,
            total_amount_expended="210000000",
            audit_year="2019",
            cognizant_agency=BASE_COG,
        )
        gen.save()
        migration_inspection_record = baker.make(
            MigrationInspectionRecord,
            report_id=gen.report_id,
            dbkey=RESOLVABLE_DBKEY_WITH_BASELINE,
            audit_year="2022",
        )
        migration_inspection_record.save()

        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, BASE_COG)
        self.assertEqual(over_agency, None)

    def test_cog_assignment_with_uei_in_baseline_and_overris(self):
        BASE_UEI = "UEI1"
        BASE_EIN = "EIN1"
        BASE_COG = "00"

        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = BASE_UEI
        sac.general_information["ein"] = BASE_EIN
        sac.general_information["cognizant_agency"] = BASE_COG
        sac.report_id = "9991-09-GSAFAC-0000201851"
        sac.save()

        cog_agency, _ = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
        record_cog_assignment(sac.report_id, sac.submitted_by, cog_agency)
        cas = CognizantAssignment.objects.all()
        self.assertEqual(len(cas), 1)

        sac = SingleAuditChecklist.objects.get(report_id=sac.report_id)
        self.assertEqual(sac.cognizant_agency, cog_agency)

        oberride_cog = "01"
        CognizantAssignment(
            report_id=sac.report_id,
            cognizant_agency=oberride_cog,
            assignor_email="test_cog_over   @test.gov",
            override_comment="test_cog_over",
        ).save()
        cas = CognizantAssignment.objects.all()
        self.assertEqual(len(cas), 2)

        sac = SingleAuditChecklist.objects.get(report_id=sac.report_id)
        self.assertEqual(sac.cognizant_agency, oberride_cog)

        # a re-run ahould create a third assignmenet
        sac.cognizant_agency = None
        sac.save()
        cog_agency, _ = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.ein,
            sac.auditee_uei,
            sac.general_information["audit_year"],
        )
        record_cog_assignment(sac.report_id, sac.submitted_by, cog_agency)
        sac = SingleAuditChecklist.objects.get(report_id=sac.report_id)
        self.assertEqual(sac.cognizant_agency, cog_agency)

    def test_cog_assignment_for_2024_audit(self):
        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = "ZQGGHJH74DW7"
        sac.general_information["ein"] = UNIQUE_EIN_WITHOUT_DBKEY
        sac.general_information["report_id"] = "1111-03-GSAFAC-0000202460"
        sac.general_information["auditee_fiscal_period_end"] = "2024-05-31"
        sac.general_information["auditee_fiscal_period_start"] = "2023-06-01"
        sac.report_id = "1111-03-GSAFAC-0000202460"
        sac.general_information["audit_year"] = "2024"

        gen = baker.make(
            General,
            report_id="1111-03-GSAFAC-0000202460",
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            total_amount_expended="210000000",
            audit_year="2024",
        )
        gen.save()

        for i in range(6):
            cfda = baker.make(
                FederalAward,
                report_id=gen,
                federal_agency_prefix="84",
                federal_award_extension="032",
                amount_expended=10_000_000 * i,
                is_direct="Y",
            )
            cfda.save()

        sac.save()

        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.general_information["ein"],
            sac.general_information["auditee_uei"],
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "84")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_w_baseline(self):
        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = "ZQGGHJH74DW7"
        sac.general_information["ein"] = UNIQUE_EIN_WITHOUT_DBKEY
        sac.general_information["report_id"] = "1111-03-GSAFAC-0000202760"
        sac.general_information["auditee_fiscal_period_end"] = "2027-05-31"
        sac.general_information["auditee_fiscal_period_start"] = "2026-06-01"
        sac.report_id = "1111-03-GSAFAC-0000202760"
        sac.general_information["audit_year"] = "2027"

        gen = baker.make(
            General,
            report_id="1111-03-GSAFAC-0000202460",
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            total_amount_expended="210000000",
            audit_year="2024",
            cognizant_agency="24",
        )
        gen.save()

        for i in range(6):
            cfda = baker.make(
                FederalAward,
                report_id=gen,
                federal_agency_prefix="14",
                federal_award_extension="032",
                amount_expended=10_000_000 * i,
                is_direct="Y",
            )
            cfda.save()

        sac.save()

        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.general_information["ein"],
            sac.general_information["auditee_uei"],
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "24")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_no_baseline(self):
        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = "ZQGGHJH74DW8"
        sac.general_information["ein"] = "EI27NOBAS"
        sac.general_information["report_id"] = "1111-03-GSAFAC-0000202761"
        sac.general_information["auditee_fiscal_period_end"] = "2027-05-31"
        sac.general_information["auditee_fiscal_period_start"] = "2026-06-01"
        sac.report_id = "1111-03-GSAFAC-0000202761"
        sac.general_information["audit_year"] = "2027"

        gen = baker.make(
            General,
            report_id="1111-03-GSAFAC-0000202761",
            auditee_ein="EI27NOBAS",
            auditee_uei="ZQGGHJH74DW8",
            total_amount_expended="210000000",
            audit_year="2027",
        )
        gen.save()

        for i in range(6):
            cfda = baker.make(
                FederalAward,
                report_id=gen,
                federal_agency_prefix="10",
                federal_award_extension="032",
                amount_expended=10_000_000 * i,
                is_direct="Y",
            )
            cfda.save()

        sac.save()

        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.general_information["ein"],
            sac.general_information["auditee_uei"],
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_w_base_to_2026_cog(self):
        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = "ZQGGHJH74DW7"
        sac.general_information["ein"] = UNIQUE_EIN_WITHOUT_DBKEY
        sac.general_information["report_id"] = "1111-03-GSAFAC-0000202760"
        sac.general_information["auditee_fiscal_period_end"] = "2027-05-31"
        sac.general_information["auditee_fiscal_period_start"] = "2026-06-01"
        sac.report_id = "1111-03-GSAFAC-0000202760"
        sac.general_information["audit_year"] = "2027"

        gen = baker.make(
            General,
            report_id="1111-03-GSAFAC-0000202460",
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            total_amount_expended="210000000",
            audit_year="2024",
            cognizant_agency="24",
        )
        gen.save()

        gen = baker.make(
            General,
            report_id="1111-03-GSAFAC-0000202560",
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            total_amount_expended="200000000",
            audit_year="2025",
            cognizant_agency="14",
        )
        gen.save()

        gen = baker.make(
            General,
            report_id="1111-03-GSAFAC-0000202660",
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            total_amount_expended="200000000",
            audit_year="2026",
            cognizant_agency="04",
        )
        gen.save()

        for i in range(6):
            cfda = baker.make(
                FederalAward,
                report_id=gen,
                federal_agency_prefix="14",
                federal_award_extension="032",
                amount_expended=10_000_000 * i,
                is_direct="Y",
            )
            cfda.save()

        sac.save()

        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.general_information["ein"],
            sac.general_information["auditee_uei"],
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "04")
        self.assertEqual(over_agency, None)

    def test_cog_assignment_for_2027_no_base_to_2026(self):
        sac = self._fake_sac()
        sac.general_information["auditee_uei"] = "ZQGGHJH74DW7"
        sac.general_information["ein"] = UNIQUE_EIN_WITHOUT_DBKEY
        sac.general_information["report_id"] = "1111-03-GSAFAC-0000202760"
        sac.general_information["auditee_fiscal_period_end"] = "2027-05-31"
        sac.general_information["auditee_fiscal_period_start"] = "2026-06-01"
        sac.report_id = "1111-03-GSAFAC-0000202760"
        sac.general_information["audit_year"] = "2027"

        gen = baker.make(
            General,
            report_id="1111-03-GSAFAC-0000202060",
            auditee_ein=UNIQUE_EIN_WITHOUT_DBKEY,
            auditee_uei="ZQGGHJH74DW7",
            total_amount_expended="210000000",
            audit_year="2020",
            cognizant_agency="34",
        )
        gen.save()

        for i in range(6):
            cfda = baker.make(
                FederalAward,
                report_id=gen,
                federal_agency_prefix="14",
                federal_award_extension="032",
                amount_expended=10_000_000 * i,
                is_direct="Y",
            )
            cfda.save()

        sac.save()

        cog_agency, over_agency = compute_cog_over(
            sac.federal_awards,
            sac.submission_status,
            sac.general_information["ein"],
            sac.general_information["auditee_uei"],
            sac.general_information["audit_year"],
        )
        self.assertEqual(cog_agency, "10")
        self.assertEqual(over_agency, None)
