from django.test import TestCase

from model_bakery import baker
from faker import Faker

from .models import SingleAuditChecklist, User
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    Passthrough,
    Note,
    FindingText,
    CapText,
    SecondaryAuditor,
)
from audit.etl import ETL


class ETLTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
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
                        "award_reference": "ABC123",
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
                    }
                ],
                "total_amount_expended": 9000,
            }
        }
        findings_uniform_guidance = {
            "FindingsUniformGuidance": {
                "auditee_uei": "AAA123456BBB",
                "findings_uniform_guidance_entries": [
                    {
                        "award_reference": "ABC123",
                        "seq_number": 1,
                        "program": {
                            "program_name": "N/A",
                            "federal_agency_prefix": "12",
                            "three_digit_extension": "123",
                            "compliance_requirement": "A",
                            "additional_award_identification": "egd",
                        },
                        "findings": {
                            "is_valid": "Y",
                            "prior_references": "2020-010",
                            "reference_number": "2021-001",
                            "repeat_prior_reference": "Y",
                        },
                        "other_matters": "N",
                        "other_findings": "N",
                        "modified_opinion": "Y",
                        "questioned_costs": "N",
                        "material_weakness": "N",
                        "significant_deficiency": "N",
                    },
                    {
                        "award_reference": "ABC123",
                        "seq_number": 2,
                        "program": {
                            "program_name": "N/A",
                            "federal_agency_prefix": "10",
                            "three_digit_extension": "123",
                            "compliance_requirement": "A",
                            "additional_award_identification": "egd",
                        },
                        "findings": {
                            "is_valid": "Y",
                            "reference_number": "2021-002",
                            "repeat_prior_reference": "N",
                        },
                        "other_matters": "N",
                        "other_findings": "N",
                        "modified_opinion": "Y",
                        "questioned_costs": "N",
                        "material_weakness": "N",
                        "significant_deficiency": "N",
                    },
                    {
                        "award_reference": "ABC123",
                        "seq_number": 3,
                        "program": {
                            "program_name": "N/A",
                            "federal_agency_prefix": "10",
                            "three_digit_extension": "123",
                            "compliance_requirement": "A",
                            "additional_award_identification": "egd",
                        },
                        "findings": {
                            "is_valid": "Y",
                            "reference_number": "2021-003",
                            "repeat_prior_reference": "N",
                        },
                        "other_matters": "N",
                        "other_findings": "N",
                        "modified_opinion": "Y",
                        "questioned_costs": "N",
                        "material_weakness": "N",
                        "significant_deficiency": "N",
                    },
                    {
                        "award_reference": "ABC123",
                        "seq_number": 4,
                        "program": {
                            "program_name": "N/A",
                            "federal_agency_prefix": "10",
                            "three_digit_extension": "123",
                            "compliance_requirement": "A",
                            "additional_award_identification": "egd",
                        },
                        "findings": {
                            "is_valid": "Y",
                            "reference_number": "2021-004",
                            "repeat_prior_reference": "N",
                        },
                        "other_matters": "N",
                        "other_findings": "N",
                        "modified_opinion": "Y",
                        "questioned_costs": "N",
                        "material_weakness": "N",
                        "significant_deficiency": "N",
                    },
                ],
            }
        }
        notes_to_sefa = {
            "NotesToSefa": {
                "auditee_uei": "AAA123456BBB",
                "accounting_policies": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \nFusce in ipsum tempus, eleifend ipsum id, dignissim ipso lorem. Proin vel quam non metus placerat semper nec in nisi.",
                "is_minimis_rate_used": "Y",
                "rate_explained": "Ipsum lorem ipsum dolor sit amet, consectetur adipiscing elit. \nInteger nec elit sed est malesuada fermentum vitae in odio. In hac habitasse platea dictumst. Nunc ut tincidunt quam.",
                "notes_to_sefa_entries": [
                    {
                        "note_title": "First Note",
                        "note_content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \nVestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Phasellus nec tortor ut ligula sollicitudin euismod.",
                        "seq_number": 1,
                    },
                ],
            }
        }
        findings_text = {
            "FindingsText": {
                "auditee_uei": "AAA123456BBB",
                "findings_text_entries": [
                    {
                        "contains_chart_or_table": "N",
                        "text_of_finding": "This is an audit finding",
                        "reference_number": "2023-123",
                    },
                ],
            }
        }
        corrective_action_plan = {
            "CorrectiveActionPlan": {
                "auditee_uei": "AAA123456BBB",
                "corrective_action_plan_entries": [
                    {
                        "contains_chart_or_table": "N",
                        "planned_action": "This is an action",
                        "reference_number": "2023-111",
                    },
                ],
            }
        }

        sac = SingleAuditChecklist.objects.create(
            submitted_by=user,
            general_information=general_information,
            federal_awards=federal_awards,
            findings_uniform_guidance=findings_uniform_guidance,
            notes_to_sefa=notes_to_sefa,
            findings_text=findings_text,
            corrective_action_plan=corrective_action_plan,
            secondary_auditors=self._fake_secondary_auditors(),
            # audit_information=self._fake_audit_information(), TODO Un comment when frontend is done
        )
        sac.save()
        self.sac = sac

        self.etl = ETL(self.sac)
        self.report_id = sac.report_id

    def _fake_secondary_auditors(self):
        fake = Faker()
        secondary_auditors = {
            "SecondaryAuditors": {
                "secondary_auditors_entries": {
                    "items": [
                        {
                            "secondary_auditor_seq_number": i,
                            "secondary_auditor_address_street": fake.street_address(),
                            "secondary_auditor_address_city": fake.city(),
                            "secondary_auditor_address_state": fake.state_abbr(
                                include_territories=False
                            ),
                            "secondary_auditor_address_zipcode": fake.postalcode(),
                            # "secondary_auditor_country": fake.country(),
                            "secondary_auditor_ein": fake.ssn().replace("-", ""),
                            "secondary_auditor_name": fake.company(),
                            "secondary_auditor_contact_name": fake.name(),
                            "secondary_auditor_contact_title": fake.job(),
                            "secondary_auditor_contact_email": fake.ascii_email(),
                            "secondary_auditor_contact_phone": fake.basic_phone_number(),
                        }
                        for i in range(1, 3)
                    ]
                }
            }
        }
        return secondary_auditors

    def _fake_audit_information(self):
        fake = Faker()

        audit_information = {
            "dollar_threshold": 10345.45,
            "gaap_results": fake.word(),
            "is_going_concern_included": "Y" if fake.boolean() else "N",
            "is_internal_control_deficiency_disclosed": "Y" if fake.boolean() else "N",
            "is_internal_control_material_weakness_disclosed": "Y"
            if fake.boolean()
            else "N",
            "is_material_noncompliance_disclosed": "Y" if fake.boolean() else "N",
            "is_aicpa_audit_guide_included": "Y" if fake.boolean() else "N",
            "is_low_risk_auditee": "Y" if fake.boolean() else "N",
            "agencies": fake.word(),
        }
        return audit_information

    def test_load_general(self):
        self.etl.load_general()
        generals = General.objects.all()
        self.assertEqual(len(generals), 1)
        general = generals.first()
        self.assertEqual(self.report_id, general.report_id)

    def test_load_federal_award(self):
        self.etl.load_federal_award()
        federal_awards = FederalAward.objects.all()
        self.assertEqual(len(federal_awards), 1)
        federal_award = federal_awards.first()
        self.assertEqual(self.report_id, federal_award.report_id)

    def test_load_findings(self):
        self.etl.load_findings()
        findings = Finding.objects.all()
        self.assertEqual(len(findings), 4)
        finding = findings.first()
        self.assertEqual(self.report_id, finding.report_id)

    def test_load_passthrough(self):
        self.etl.load_passthrough()
        passthroughs = Passthrough.objects.all()
        self.assertEqual(len(passthroughs), 1)
        passthrough = passthroughs.first()
        self.assertEqual(self.report_id, passthrough.report_id)

    def test_load_notes(self):
        self.etl.load_note()
        notes = Note.objects.all()
        self.assertEqual(len(notes), 1)
        note = notes.first()
        self.assertEqual(self.report_id, note.report_id)

    def test_load_finding_texts(self):
        self.etl.load_finding_texts()
        finding_texts = FindingText.objects.all()
        self.assertEqual(len(finding_texts), 1)
        finding_text = finding_texts.first()
        self.assertEqual(self.report_id, finding_text.report_id)

    def test_load_captext(self):
        self.etl.load_captext()
        cap_texts = CapText.objects.all()
        self.assertEqual(len(cap_texts), 1)
        cap_text = cap_texts.first()
        self.assertEqual(self.report_id, cap_text.report_id)

    def test_load_sec_auditor(self):
        self.etl.load_all()
        sec_auditor = SecondaryAuditor.objects.first()
        # print("SecondaryAuditor:", sec_auditor.auditor_name)
        self.assertEquals(self.sac.report_id, sec_auditor.report_id)

    # TODO rename to test_load_audit once frontend is available
    def todo_load_aidit_information(self):
        self.etl.load_all()
        general = General.objects.first()
        sac = SingleAuditChecklist.objects.first()
        print("general gaap_results:", general.gaap_results, sac.audit_information)
        self.assertEquals(sac.audit_information["gaap_results"], general.gaap_results)
