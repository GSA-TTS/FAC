from django.test import TestCase
from model_bakery import baker

from audit.models import Audit, SingleAuditChecklist
from audit.models.utils import (
    validate_audit_consistency,
)


class TestValidateAuditConsistency(TestCase):
    """Tests for validate_audit_consistency"""

    def test_simple_valid(self):
        """Trivial valid case"""
        audit = baker.make(Audit, version=0)
        baker.make(SingleAuditChecklist, report_id=audit.report_id)
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_simple_invalid(self):
        """
        Generate a difference when the values for a simple field don't
        match
        """
        audit = baker.make(Audit, version=0)
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.data_source = "foo"
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(
            result[1][0],
            {"field": "data_source", "sac_value": "foo", "audit_value": "GSAFAC"},
        )
        self.assertFalse(result[0])

    def test_json_valid(self):
        """Simple valid case for a JSON field"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"general_information": {"a": 1}}
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = {"a": 1}
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_json_invalid(self):
        """Generate a difference when a value differs between SAC and SOT"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"general_information": {"a": 1}}
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = {"a": 2}
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {
                "audit_value": {"a": 1},
                "error": "Field JSON does not match",
                "field": "general_information",
                "sac_value": {"a": 2},
            },
        )
        self.assertFalse(result[0])

    def test_json_audit_none_invalid(self):
        """
        Generate a difference when a field is empty in SAC, but not in
        SOT
        """
        audit = baker.make(Audit, version=0)
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = {"a": 1}
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {
                "field": "general_information",
                "error": "Field is empty in Audit, but not in SAC",
                "sac_value": {"a": 1},
                "audit_value": None,
            },
        )
        self.assertFalse(result[0])

    def test_json_sac_none_invalid(self):
        """
        Generate a difference when a field is empty in SOT, but not in
        SAC
        """
        audit = baker.make(Audit, version=0)
        audit.audit = {"general_information": {"a": 1}}
        audit.save()
        baker.make(SingleAuditChecklist, report_id=audit.report_id)
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {
                "field": "general_information",
                "error": "Field is empty in SAC, but not in Audit",
                "sac_value": None,
                "audit_value": {"a": 1},
            },
        )
        self.assertFalse(result[0])

    def test_has_tribal_data_consent(self):
        """Valid case when tribal data consent exists"""
        audit = baker.make(Audit, version=0)
        audit.organization_type = "tribal"
        audit.audit = {"tribal_data_consent": {"foo": "bar"}}
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.tribal_data_consent = {"foo": "bar"}
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_no_tribal_data_consent(self):
        """Valid case when tribal data consent doesn't exist"""
        audit = baker.make(Audit, version=0)
        audit.organization_type = "non-tribal"
        audit.audit = {"tribal_data_consent": {}}
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.tribal_data_consent = None
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_meta(self):
        """
        Valid case where SAC fields that only contain a Meta field is
        ignored
        """
        audit = baker.make(Audit, version=0)
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.findings_text = {"Meta": {"section_name": "FindingsText"}}
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_findings_text(self):
        """Valid case for findings_text"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"findings_text": [{"foo": "bar"}]}
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.findings_text = {
            "FindingsText": {
                "findings_text_entries": [
                    {
                        "foo": "bar",
                    }
                ],
            },
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_findings_text_none(self):
        """
        Valid case for findings_text where SOT and SAC have no data
        """
        audit = baker.make(Audit, version=0)
        audit.audit = {}
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.findings_text = {
            "FindingsText": {},
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_corrective_action_plan(self):
        """Valid case for corrective_action_plan"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"corrective_action_plan": [{"foo": "bar"}]}
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.corrective_action_plan = {
            "CorrectiveActionPlan": {
                "corrective_action_plan_entries": [
                    {
                        "foo": "bar",
                    }
                ],
            },
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_corrective_action_plan_none(self):
        """
        Valid case for corrective_action_plan where SOT and SAC have no data
        """
        audit = baker.make(Audit, version=0)
        audit.audit = {}
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.corrective_action_plan = {
            "CorrectiveActionPlan": {},
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_additional_eins(self):
        """Valid case for additional_eins"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"additional_eins": ["42"]}
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.additional_eins = {
            "AdditionalEINs": {"additional_eins_entries": [{"additional_ein": "42"}]}
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_additional_eins_invalid(self):
        """Invalid case for additional_eins"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"additional_eins": ["42"]}
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.additional_eins = {
            "AdditionalEINs": {"additional_eins_entries": [{"additional_ein": "0"}]}
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {
                "field": "additional_eins",
                "sac_value": ["0"],
                "audit_value": ["42"],
                "error": "Values don't match between SAC and Audit",
            },
        )
        self.assertFalse(result[0])

    def test_additional_ueis(self):
        """Valid case for additional_ueis"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"additional_ueis": ["42"]}
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.additional_ueis = {
            "AdditionalUEIs": {"additional_ueis_entries": [{"additional_uei": "42"}]}
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_additional_ueis_invalid(self):
        """Invalid case for additional_ueis"""
        audit = baker.make(Audit, version=0)
        audit.audit = {"additional_ueis": ["42"]}
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.additional_ueis = {
            "AdditionalUEIs": {"additional_ueis_entries": [{"additional_uei": "0"}]}
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {
                "field": "additional_ueis",
                "sac_value": ["0"],
                "audit_value": ["42"],
                "error": "Values don't match between SAC and Audit",
            },
        )
        self.assertFalse(result[0])

    def test_secondary_auditors(self):
        """Valid case for secondary_auditors"""
        audit = baker.make(Audit, version=0)
        audit.audit = {
            "secondary_auditors": [
                {
                    "secondary_auditor_ein": "42",
                }
            ],
        }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.secondary_auditors = {
            "SecondaryAuditors": {
                "secondary_auditors_entries": [{"secondary_auditor_ein": "42"}]
            }
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_secondary_auditors_invalid(self):
        """Invalid case for secondary_auditors"""
        audit = baker.make(Audit, version=0)
        audit.audit = {
            "secondary_auditors": [
                {
                    "secondary_auditor_ein": "42",
                }
            ],
        }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.secondary_auditors = {
            "SecondaryAuditors": {
                "secondary_auditors_entries": [{"secondary_auditor_ein": "0"}]
            }
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {
                "field": "secondary_auditors",
                "sac_value": ["0"],
                "audit_value": ["42"],
                "error": "Values don't match between SAC and Audit",
            },
        )
        self.assertFalse(result[0])

    def test_cog_over(self):
        """Valid case for a cog/over not during real-time validation"""
        audit = baker.make(Audit, version=0)
        audit.cognizant_agency = "1"
        audit.oversight_agency = "2"
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.cognizant_agency = "1"
        sac.oversight_agency = "2"
        sac.save()
        result = validate_audit_consistency(audit, is_real_time=False)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_cog_over_invalid(self):
        """Valid case for a cog/over not during real-time validation"""
        audit = baker.make(Audit, version=0)
        audit.cognizant_agency = "1"
        audit.oversight_agency = "2"
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.cognizant_agency = "a"
        sac.oversight_agency = "b"
        sac.save()
        result = validate_audit_consistency(audit, is_real_time=False)
        self.assertEqual(
            result[1][0],
            {"field": "cognizant_agency", "sac_value": "a", "audit_value": "1"},
            {"field": "oversight_agency", "sac_value": "b", "audit_value": "2"},
        )
        self.assertFalse(result[0])

    def test_cog_over_real_time(self):
        """Valid case for a cog/over during real-time validation"""
        audit = baker.make(Audit, version=0)
        audit.cognizant_agency = None
        audit.oversight_agency = None
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.cognizant_agency = "1"
        sac.oversight_agency = "2"
        sac.save()
        result = validate_audit_consistency(audit, is_real_time=True)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_federal_awards_valid(self):
        """Simple valid case for federal_awards"""
        audit = baker.make(Audit, version=0)
        audit.audit = {
            "federal_awards": {
                "awards": [{"foo": 1}, {"foo": 2}],
                "total_amount_expended": 42,
            },
        }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.federal_awards = {
            "Meta": {"section_name": "FederalAwards"},
            "FederalAwards": {
                "federal_awards": [{"foo": 1}, {"foo": 2}],
                "total_amount_expended": 42,
            },
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_federal_awards_invalid(self):
        """Invalid case for federal_awards where awards are misordered"""
        audit = baker.make(Audit, version=0)
        audit.audit = {
            "federal_awards": {
                "awards": [{"foo": 1}, {"foo": 2}],
                "total_amount_expended": 42,
            },
        }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.federal_awards = {
            "Meta": {"section_name": "FederalAwards"},
            "FederalAwards": {
                "federal_awards": [{"foo": 2}, {"foo": 1}],
                "total_amount_expended": 42,
            },
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {
                "audit_value": {
                    "awards": [{"foo": 1}, {"foo": 2}],
                    "total_amount_expended": 42,
                },
                "error": "Field JSON does not match",
                "field": "federal_awards",
                "sac_value": {
                    "awards": [{"foo": 2}, {"foo": 1}],
                    "total_amount_expended": 42,
                },
            },
        )
        self.assertFalse(result[0])
