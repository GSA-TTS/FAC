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
    AdditionalUei,
    AdditionalEin,
)
from audit.etl import ETL


class ETLTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def setUp(self):
        self.user = baker.make(User)

        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
            findings_uniform_guidance=self._fake_findings_uniform_guidance(),
            notes_to_sefa=self._fake_notes_to_sefa(),
            findings_text=self._fake_findings_text(),
            corrective_action_plan=self._fake_corrective_action_plan(),
            secondary_auditors=self._fake_secondary_auditors(),
            additional_ueis=self._fake_additional_ueis(),
        )
        sac.save()
        self.sac = sac
        self.etl = ETL(self.sac)
        self.report_id = sac.report_id

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
            "audit_period_other_months": None,
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
    def _fake_federal_awards():
        return {
            "FederalAwards": {
                "auditee_uei": "ABC123DEF456",
                "federal_awards": [
                    {
                        "award_reference": "ABC123",
                        "cluster": {"cluster_name": "N/A", "cluster_total": 0},
                        "program": {
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

    @staticmethod
    def _fake_findings_uniform_guidance(reference_number: int = 1):
        return {
            "FindingsUniformGuidance": {
                "auditee_uei": "AAA123456BBB",
                "findings_uniform_guidance_entries": [
                    {
                        "seq_number": i,
                        "program": {
                            "award_reference": "ABC123",
                            "program_name": "N/A",
                            "federal_agency_prefix": "12",
                            "three_digit_extension": "123",
                            "compliance_requirement": "A",
                            "additional_award_identification": "egd",
                        },
                        "findings": {
                            "is_valid": "Y",
                            "prior_references": "2020-010",
                            "reference_number": f"2021-{i:03d}",
                            "repeat_prior_reference": "Y",
                        },
                        "other_matters": "N",
                        "other_findings": "N",
                        "modified_opinion": "Y",
                        "questioned_costs": "N",
                        "material_weakness": "N",
                        "significant_deficiency": "N",
                    }
                    for i in range(1, 5)
                ],
            }
        }

    @staticmethod
    def _fake_notes_to_sefa():
        return {
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

    @staticmethod
    def _fake_findings_text(reference_number: int = 123):
        return {
            "FindingsText": {
                "auditee_uei": "AAA123456BBB",
                "findings_text_entries": [
                    {
                        "contains_chart_or_table": "N",
                        "text_of_finding": "This is an audit finding",
                        "reference_number": f"2023-{reference_number:03d}",
                    },
                ],
            }
        }

    @staticmethod
    def _fake_corrective_action_plan():
        return {
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

    @staticmethod
    def _fake_secondary_auditors():
        fake = Faker()
        secondary_auditors = {
            "SecondaryAuditors": {
                "secondary_auditors_entries": [
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
        return secondary_auditors

    @staticmethod
    def _fake_audit_information():
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

    @staticmethod
    def _fake_additional_ueis():
        return {
            "AdditionalUEIs": {
                "auditee_uei": "ZQGGHJH74DW7",
                "additional_ueis_entries": [
                    {"additional_uei": "ABA123456BBC"},
                    {"additional_uei": "ACA123456BBD"},
                ],
            }
        }

    @staticmethod
    def _fake_additional_eins():
        return {
            "AdditionalEINs": {
                "auditee_uei": "ZQGGHJH74DW7",
                "additional_eins_entries": [
                    {"additional_ein": "874151234"},
                    {"additional_ein": "876505678"},
                ],
            }
        }

    def test_load_general(self):
        self.etl.load_general()
        generals = General.objects.all()
        self.assertEqual(len(generals), 1)
        general = generals.first()
        self.assertEqual(self.report_id, general.report_id)

    def test_load_award_before_general_should_fail(self):
        self.etl.load_federal_award()
        federal_awards = FederalAward.objects.all()
        self.assertEqual(len(federal_awards), 0)

    def test_load_federal_award(self):
        self.etl.load_general()
        self.etl.load_federal_award()
        federal_awards = FederalAward.objects.all()
        self.assertEqual(len(federal_awards), 1)
        federal_award = federal_awards.first()
        self.assertEqual(self.report_id, federal_award.report_id)
        general = General.objects.first()
        self.assertEqual(
            general.total_amount_expended,
            self.sac.federal_awards["FederalAwards"].get("total_amount_expended"),
        )

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
        self.etl.load_secondary_auditor()
        sec_auditor = SecondaryAuditor.objects.first()
        self.assertIsNone(sec_auditor)
        self.etl.load_general()
        self.etl.load_secondary_auditor()
        sec_auditor = SecondaryAuditor.objects.first()

        self.assertEquals(self.sac.report_id, sec_auditor.report_id)

    def todo_load_audit_information(self):
        self.etl.load_audit_info()
        general = General.objects.first()
        sac = SingleAuditChecklist.objects.first()
        self.assertEquals(sac.audit_information["gaap_results"], general.gaap_results)

    def test_load_all(self):
        """On a happy path through load_all(), item(s) should be added to all of the
        tables."""
        len_general = len(General.objects.all())
        len_captext = len(CapText.objects.all())
        len_additional_ueis = len(AdditionalUei.objects.all())
        len_additional_eins = len(AdditionalEin.objects.all())
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
            findings_uniform_guidance=self._fake_findings_uniform_guidance(),
            notes_to_sefa=self._fake_notes_to_sefa(),
            findings_text=self._fake_findings_text(reference_number=2),
            corrective_action_plan=self._fake_corrective_action_plan(),
            secondary_auditors=self._fake_secondary_auditors(),
            additional_ueis=self._fake_additional_ueis(),
            additional_eins=self._fake_additional_eins(),
            audit_information=self._fake_audit_information(),  # TODO: Uncomment when SingleAuditChecklist adds audit_information
        )
        sac.save()
        self.sac = sac
        self.etl = ETL(self.sac)
        self.report_id = sac.report_id
        self.etl.load_all()
        self.assertLess(len_general, len(General.objects.all()))
        self.assertLess(len_captext, len(CapText.objects.all()))
        self.assertLess(len_additional_ueis, len(AdditionalUei.objects.all()))
        self.assertLess(len_additional_eins, len(AdditionalEin.objects.all()))

    def test_load_all_with_errors_1(self):
        """IWe should not encounter a key error in general,
        an error that would prevent the loading of a child table
        """
        len_general = len(General.objects.all())
        len_captext = len(CapText.objects.all())
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
            findings_uniform_guidance=self._fake_findings_uniform_guidance(),
            notes_to_sefa=self._fake_notes_to_sefa(),
            findings_text=self._fake_findings_text(reference_number=3),
            corrective_action_plan=self._fake_corrective_action_plan(),
            secondary_auditors=self._fake_secondary_auditors(),
            additional_ueis=self._fake_additional_ueis(),
        )
        sac.general_information.pop("auditee_contact_name")
        sac.save()
        self.sac = sac
        self.etl = ETL(self.sac)
        self.report_id = sac.report_id
        self.etl.load_all()
        self.assertLess(len_general, len(General.objects.all()))
        self.assertLess(len_captext, len(CapText.objects.all()))

    def test_load_all_with_errors_2(self):
        """If we encounter a KeyError on CapText (the last table to be loaded), we
        should still load all the other tables, but nothing should be loaded to CapText.
        """
        len_general = len(General.objects.all())
        len_captext = len(CapText.objects.all())
        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=self._fake_general(),
            federal_awards=self._fake_federal_awards(),
            findings_uniform_guidance=self._fake_findings_uniform_guidance(),
            notes_to_sefa=self._fake_notes_to_sefa(),
            findings_text=self._fake_findings_text(reference_number=3),
            corrective_action_plan=self._fake_corrective_action_plan(),
            secondary_auditors=self._fake_secondary_auditors(),
            additional_ueis=self._fake_additional_ueis(),
        )
        sac.corrective_action_plan.pop("CorrectiveActionPlan")
        sac.save()
        self.sac = sac
        self.etl = ETL(self.sac)
        self.report_id = sac.report_id
        self.etl.load_all()
        self.assertLess(len_general, len(General.objects.all()))
        self.assertEqual(len_captext, len(CapText.objects.all()))
