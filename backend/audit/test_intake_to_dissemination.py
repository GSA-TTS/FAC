from datetime import datetime, time, timezone, timedelta
import json
from django.test import TestCase
from model_bakery import baker
from faker import Faker

from audit.models import SingleAuditChecklist, User
from audit.intake_to_dissemination import IntakeToDissemination
from audit.test_views import AUDIT_JSON_FIXTURES, _load_json
from audit.utils import Util
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    Passthrough,
    Note,
    FindingText,
    CapText,
    SecondaryAuditor,
    AdditionalEin,
    AdditionalUei,
)


def _set_transitions_hour(sac, hour):
    statuses = [
        SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
        SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
        SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
        SingleAuditChecklist.STATUS.SUBMITTED,
    ]
    # Get the current time in UTC
    current = datetime.now(timezone.utc).date()
    transition_date = datetime.combine(
        current,
        time(
            hour=hour,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        ),
    )

    for status in statuses:
        sac.transition_date.append(transition_date)
        sac.transition_name.append(status)
        # Increment the minute by 2
        transition_date += timedelta(minutes=2)

    return sac


class IntakeToDisseminationTests(TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def _run_state_transition(self, sac):
        statuses = [
            SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
            SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
            SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
            SingleAuditChecklist.STATUS.SUBMITTED,
        ]
        # Get the current time in UTC
        transition_date = datetime.now(timezone.utc)

        for status in statuses:
            sac.transition_date.append(transition_date)
            sac.transition_name.append(status)
            # Increment the minute by 2
            transition_date += timedelta(minutes=2)

    def _create_sac(
        self,
        reference_number=None,
        user_provided_organization_type=None,
        cognizant_agency=None,
        oversight_agency=None,
        privacy_flag=None,
    ):
        if reference_number:
            findings_text_data = self._fake_findings_text(
                reference_number=reference_number
            )
        else:
            findings_text_data = self._fake_findings_text()

        if user_provided_organization_type:
            general_data = self._fake_general(
                user_provided_organization_type=user_provided_organization_type
            )
        else:
            general_data = self._fake_general()

        sac = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            general_information=general_data,
            federal_awards=self._fake_federal_awards(),
            findings_uniform_guidance=self._fake_findings_uniform_guidance(),
            notes_to_sefa=self._fake_notes_to_sefa(),
            findings_text=findings_text_data,
            corrective_action_plan=self._fake_corrective_action_plan(),
            secondary_auditors=self._fake_secondary_auditors(),
            additional_ueis=self._fake_additional_ueis(),
            additional_eins=self._fake_additional_eins(),
            audit_information=self._fake_audit_information(),
            auditee_certification=self._fake_auditee_certification(),
            auditor_certification=self._fake_auditor_certification(),
            tribal_data_consent=self._fake_tribal_data_consent(privacy_flag),
            cognizant_agency=cognizant_agency,
            oversight_agency=oversight_agency,
        )
        return sac

    def setUp(self):
        self.user = baker.make(User)

        sac = self._create_sac(cognizant_agency="42", oversight_agency="42")
        self._run_state_transition(sac)
        self.sac = sac
        self.intake_to_dissemination = IntakeToDissemination(self.sac)
        self.report_id = sac.report_id

    @staticmethod
    def _fake_general(user_provided_organization_type: str = "state"):
        fake = Faker()
        geninfofile = "general-information--test0001test--simple-pass.json"
        geninfo = _load_json(AUDIT_JSON_FIXTURES / geninfofile)

        return geninfo | {
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
            "auditor_country": "USA",
            "auditor_firm_name": fake.company(),
            "audit_period_covered": "annual",
            "audit_period_other_months": fake.random_int(min=1, max=12),
            "auditee_contact_name": fake.name(),
            "auditor_contact_name": fake.name(),
            "auditee_contact_title": "Boss",
            "auditor_contact_title": "Mega Boss",
            "multiple_eins_covered": fake.boolean(),
            "multiple_ueis_covered": fake.boolean(),
            "auditee_address_line_1": fake.street_address(),
            "auditor_address_line_1": fake.street_address(),
            "met_spending_threshold": "true",
            "auditee_fiscal_period_end": "2023-06-01",
            "ein_not_an_ssn_attestation": "true",
            "auditee_fiscal_period_start": "2022-11-01",
            "user_provided_organization_type": user_provided_organization_type,
            "auditor_ein_not_an_ssn_attestation": "true",
        }

    @staticmethod
    def _fake_auditee_certification():
        fake = Faker()
        return {
            "auditee_certification": {
                "has_no_PII": fake.boolean(),
                "has_no_BII": fake.boolean(),
                "meets_2CFR_specifications": fake.boolean(),
                "is_2CFR_compliant": fake.boolean(),
                "is_complete_and_accurate": fake.boolean(),
                "has_engaged_auditor": fake.boolean(),
                "is_issued_and_signed": fake.boolean(),
                "is_FAC_releasable": fake.boolean(),
            },
            "auditee_signature": {
                "auditee_name": fake.name(),
                "auditee_title": fake.job(),
                "auditee_certification_date_signed": fake.date(),
            },
        }

    @staticmethod
    def _fake_auditor_certification():
        fake = Faker()
        return {
            "auditor_certification": {
                "has_no_PII": fake.boolean(),
                "has_no_BII": fake.boolean(),
                "meets_2CFR_specifications": fake.boolean(),
                "is_2CFR_compliant": fake.boolean(),
                "is_complete_and_accurate": fake.boolean(),
                "has_engaged_auditor": fake.boolean(),
                "is_issued_and_signed": fake.boolean(),
                "is_FAC_releasable": fake.boolean(),
            },
            "auditor_signature": {
                "auditor_name": fake.name(),
                "auditor_title": fake.job(),
                "auditor_certification_date_signed": fake.date(),
            },
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
                            "is_major": "N",
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
                        "contains_chart_or_table": "Y",
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
            "gaap_results": json.dumps([fake.word()]),
            "is_going_concern_included": "Y" if fake.boolean() else "N",
            "is_internal_control_deficiency_disclosed": "Y" if fake.boolean() else "N",
            "is_internal_control_material_weakness_disclosed": "Y"
            if fake.boolean()
            else "N",
            "is_material_noncompliance_disclosed": "Y" if fake.boolean() else "N",
            "is_aicpa_audit_guide_included": "Y" if fake.boolean() else "N",
            "is_low_risk_auditee": "Y" if fake.boolean() else "N",
            "agencies": json.dumps([fake.word()]),
        }
        return audit_information

    @staticmethod
    def _fake_tribal_data_consent(privacy_flag=None):
        fake = Faker()

        if privacy_flag is None:
            privacy_flag = fake.boolean()

        return {
            "is_tribal_information_authorized_to_be_public": privacy_flag,
            "tribal_authorization_certifying_official_name": fake.word(),
            "tribal_authorization_certifying_official_title": fake.word(),
        }

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
                    {"additional_ein": "987654321"},
                    {"additional_ein": "123456789"},
                ],
            }
        }

    def test_load_general(self):
        self.intake_to_dissemination.load_general()
        self.intake_to_dissemination.save_dissemination_objects()
        generals = General.objects.all()
        self.assertEqual(len(generals), 1)
        general = generals.first()
        self.assertEqual(self.report_id, general.report_id)
        self.assertEqual(
            general.total_amount_expended,
            self.sac.federal_awards["FederalAwards"].get("total_amount_expended"),
        )
        self.assertEquals(
            Util.json_array_to_str(self.sac.audit_information["gaap_results"]),
            general.gaap_results,
        )

    def test_submitted_date(self):
        """
        The date of submission should be disseminated using the time in American Samoa.
        """
        hours = range(0, 24)

        for hour in hours:
            with self.subTest():
                self.setUp()
                self.sac.transition_date = []
                self.sac.transition_name = []
                sac = _set_transitions_hour(self.sac, hour)
                sac.save()
                self.intake_to_dissemination.load_general()
                self.intake_to_dissemination.save_dissemination_objects()
                generals = General.objects.all()
                self.assertEqual(len(generals), 1)
                general = generals.first()

                # Get the sac submitted date
                subdate = self.sac.get_transition_date(self.sac.STATUS.SUBMITTED)
                # Calculate the date at UTC-11 (the American Samoa timezone does not do DST)
                date_in_american_samoa = (subdate - timedelta(hours=11)).date()

                self.assertEqual(general.submitted_date, date_in_american_samoa)
                general.delete()

    def _setup_and_test_privacy_flag(self, flag):
        """Common setup and test logic for tribal data privacy flag tests."""

        sac = self._create_sac(
            privacy_flag=flag,
            user_provided_organization_type="tribal",
            cognizant_agency="xx",
            oversight_agency="",
        )
        self._run_state_transition(sac)
        self.intake_to_dissemination = IntakeToDissemination(sac)
        self.intake_to_dissemination.load_all()
        self.intake_to_dissemination.save_dissemination_objects()
        general = General.objects.first()
        self.assertEqual(general.entity_type, "tribal")
        self.assertEqual(general.is_public, flag)

    def test_tribal_data_is_public_when_authorized(self):
        """Test that tribal data privacy flag is enabled when user has authorized it to be public."""
        self._setup_and_test_privacy_flag(True)

    def test_tribal_data_is_private_when_not_authorized(self):
        """Test that tribal data privacy flag is disabled when user has not authorized it to be public."""
        self._setup_and_test_privacy_flag(False)

    def test_load_federal_award(self):
        self.intake_to_dissemination.load_federal_award()
        self.intake_to_dissemination.save_dissemination_objects()
        federal_awards = FederalAward.objects.all()
        self.assertEqual(len(federal_awards), 1)
        federal_award = federal_awards.first()
        self.assertEqual(self.report_id, federal_award.report_id)
        self.assertEqual(
            federal_award.federal_program_total,
            self.sac.federal_awards["FederalAwards"]["federal_awards"][0]["program"][
                "federal_program_total"
            ],
        )

    def test_load_findings(self):
        self.intake_to_dissemination.load_findings()
        self.intake_to_dissemination.save_dissemination_objects()
        findings = Finding.objects.all()
        self.assertEqual(len(findings), 4)
        finding = findings.first()
        self.assertEqual(self.report_id, finding.report_id)

    def test_load_passthrough(self):
        self.intake_to_dissemination.load_passthrough()
        self.intake_to_dissemination.save_dissemination_objects()
        passthroughs = Passthrough.objects.all()
        self.assertEqual(len(passthroughs), 1)
        passthrough = passthroughs.first()
        self.assertEqual(self.report_id, passthrough.report_id)

    def test_load_notes(self):
        self.intake_to_dissemination.load_notes()
        self.intake_to_dissemination.save_dissemination_objects()
        notes = Note.objects.all()
        self.assertEqual(len(notes), 1)
        note = notes.first()
        self.assertEqual(self.report_id, note.report_id)

    def test_load_finding_texts(self):
        self.intake_to_dissemination.load_finding_texts()
        self.intake_to_dissemination.save_dissemination_objects()
        finding_texts = FindingText.objects.all()
        self.assertEqual(len(finding_texts), 1)
        finding_text = finding_texts.first()
        self.assertEqual(self.report_id, finding_text.report_id)

    def test_load_captext(self):
        self.intake_to_dissemination.load_captext()
        self.intake_to_dissemination.save_dissemination_objects()
        cap_texts = CapText.objects.all()
        self.assertEqual(len(cap_texts), 1)
        cap_text = cap_texts.first()
        self.assertEqual(self.report_id, cap_text.report_id)

    def test_load_sec_auditor(self):
        self.intake_to_dissemination.load_secondary_auditor()
        self.intake_to_dissemination.save_dissemination_objects()
        sec_auditor = SecondaryAuditor.objects.first()
        print(self.sac.report_id)
        print(sec_auditor.report_id)
        self.assertEquals(self.sac.report_id, sec_auditor.report_id)

    def test_load_additional_ueis(self):
        self.intake_to_dissemination.load_additional_ueis()
        self.intake_to_dissemination.save_dissemination_objects()
        dissem_ueis = [obj.additional_uei for obj in AdditionalUei.objects.all()]
        intake_ueis = [
            obj["additional_uei"]
            for obj in self.sac.additional_ueis["AdditionalUEIs"][
                "additional_ueis_entries"
            ]
        ]
        self.assertEqual(set(dissem_ueis), set(intake_ueis))

    def test_load_additional_eins(self):
        self.intake_to_dissemination.load_additional_eins()
        self.intake_to_dissemination.save_dissemination_objects()
        dissem_eins = [obj.additional_ein for obj in AdditionalEin.objects.all()]
        intake_eins = [
            obj["additional_ein"]
            for obj in self.sac.additional_eins["AdditionalEINs"][
                "additional_eins_entries"
            ]
        ]
        self.assertEqual(set(dissem_eins), set(intake_eins))

    def test_load_all(self):
        """On a happy path through load_all(), item(s) should be added to all of the
        tables."""
        len_general = len(General.objects.all())
        len_captext = len(CapText.objects.all())

        sac = self._create_sac(
            reference_number=2, cognizant_agency="xx", oversight_agency=""
        )
        self._run_state_transition(sac)
        self.sac = sac
        self.intake_to_dissemination = IntakeToDissemination(self.sac)
        self.intake_to_dissemination.load_all()
        self.intake_to_dissemination.save_dissemination_objects()
        self.report_id = sac.report_id
        self.assertLess(len_general, len(General.objects.all()))
        self.assertLess(len_captext, len(CapText.objects.all()))
        general = General.objects.first()
        self.assertNotEqual(general.entity_type, "tribal")
        self.assertEqual(general.is_public, True)

    def test_load_and_return_objects(self):
        len_general = len(General.objects.all())
        len_captext = len(CapText.objects.all())
        sac = self._create_sac(reference_number=2)
        self._run_state_transition(sac)
        self.sac = sac
        self.intake_to_dissemination = IntakeToDissemination(self.sac)
        self.report_id = sac.report_id
        self.intake_to_dissemination.load_all()
        objs = self.intake_to_dissemination.get_dissemination_objects()
        self.assertEqual(len_general, len(General.objects.all()))
        self.assertEqual(len_captext, len(CapText.objects.all()))
        keys = [
            "Generals",
            "SecondaryAuditors",
            "FederalAwards",
            "Findings",
            "FindingTexts",
            "Passthroughs",
            "CapTexts",
            "Notes",
            "Revisions",
            "AdditionalUEIs",
            "AdditionalEINs",
        ]

        for k, v in objs.items():
            self.assertTrue(k in keys, f"Key {k} not found in keys.")
            self.assertTrue(len(v) > 0, f"Value list for {k} is empty.")

            for obj in v:
                self.assertIsNotNone(obj, "Object should not be None.")
