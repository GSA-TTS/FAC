from django.test import TestCase

from model_bakery import baker

from ..models import SingleAuditChecklist, User
from dissemination.models import General, FederalAward
from .etl import ETL


class ETLTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        self.report_id = ""
        super().__init__(methodName)

    def setUp(self):
        user = baker.make(User)
        general_information = {
            "ein": "123456789",
            "audit_type": "single-audit",
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_zip": "68130",
            "auditor_ein": "234567891",
            "auditor_zip": "10123",
            "auditee_city": "Cedar City",
            "auditee_name": "INTERNATIONAL BUSINESS MACHINES CORPORATION",
            "auditor_city": "New York City",
            "is_usa_based": "true",
            "auditee_email": "e@mail.com",
            "auditee_phone": "4023001234",
            "auditee_state": "IA",
            "auditor_email": "e@mail.com",
            "auditor_phone": "4024445555",
            "auditor_state": "NY",
            "auditor_country": "United States",
            "auditor_firm_name": "Big Wigs Firm",
            "audit_period_covered": "annual",
            "auditee_contact_name": "Joe",
            "auditor_contact_name": "Big Guy",
            "auditee_contact_title": "Boss",
            "auditor_contact_title": "Mega Boss",
            "multiple_eins_covered": "false",
            "multiple_ueis_covered": "false",
            "auditee_address_line_1": "1 Main St",
            "auditor_address_line_1": "2 Main Street",
            "met_spending_threshold": "true",
            "auditee_fiscal_period_end": "2023-06-01",
            "ein_not_an_ssn_attestation": "true",
            "auditee_fiscal_period_start": "2022-11-01",
            "user_provided_organization_type": "state",
            "auditor_ein_not_an_ssn_attestation": "true",
        }
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
        sac = SingleAuditChecklist.objects.create(
            submitted_by=user,
            general_information=general_information,
            federal_awards=federal_awards,
        )
        sac.save()
        self.report_id = sac.report_id

    def test_load_general(self):
        sac = SingleAuditChecklist.objects.get(report_id=self.report_id)
        etl = ETL(sac)
        etl.load_general()
        generals = General.objects.all()
        self.assertEqual(len(generals), 1)
        general = generals.first()
        self.assertEqual(self.report_id, general.report_id)

    def test_load_federal_award(self):
        sac = SingleAuditChecklist.objects.get(report_id=self.report_id)
        etl = ETL(sac)
        etl.load_federal_award()
        federal_awards = FederalAward.objects.all()
        self.assertEqual(len(federal_awards), 1)
        federal_award = federal_awards.first()
        self.assertEqual(self.report_id, federal_award.report_id)
