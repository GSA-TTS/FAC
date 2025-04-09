from django.test import TestCase
from model_bakery import baker

from audit.models import Audit, SingleAuditChecklist
from audit.models.utils import (
  flatten_json,
  value_exists_in_audit,
  other_formats_match,
  validate_audit_consistency,
)


class TestFlattenJson(TestCase):
    """Tests for flatten_json"""
    def test_empty(self):
        test_json = {}
        expected_result = {}
        result = flatten_json(test_json)
        self.assertDictEqual(result, expected_result)

    def test_simple(self):
        test_json = { "a": 1 , "b": 2 }
        expected_result = { "a": 1 , "b": 2 }
        result = flatten_json(test_json)
        self.assertDictEqual(result, expected_result)

    def test_nested(self):
        test_json = { "a": { "b": 2 }, "c": 3 }
        expected_result = { "a.b": 2, "c": 3 }
        result = flatten_json(test_json)
        self.assertDictEqual(result, expected_result)

    def test_list(self):
        test_json = { "a": [1, 2] }
        expected_result = { "a[0]": 1 , "a[1]": 2 }
        result = flatten_json(test_json)
        self.assertDictEqual(result, expected_result)

    def test_nested_list(self):
        test_json = { "a": { "b": [1, 2] } }
        expected_result = { "a.b[0]": 1 , "a.b[1]": 2 }
        result = flatten_json(test_json)
        self.assertDictEqual(result, expected_result)


class TestValueExistsInAudit(TestCase):
    """Tests for value_exists_in_audit"""
    def test_empty(self):
        sac_path = "a"
        sac_value = 1
        test_json = {}
        expected_result = { 'found': False }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_simple(self):
        sac_path = "a"
        sac_value = 1
        test_json = { "a": 1 }
        expected_result = { 'found': True }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_nested(self):
        sac_path = "a.b"
        sac_value = 2
        test_json = { "c.b": 2 }
        expected_result = { 'found': True }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_list(self):
        sac_path = "a[0]"
        sac_value = 1
        test_json = { "a[0]": 1 }
        expected_result = { 'found': True }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_nested_list(self):
        sac_path = "a.b[0]"
        sac_value = 1
        test_json = { "a.b[0]": 1 }
        expected_result = { 'found': True }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_list_different_index(self):
        """
        A value that matches but has a different position in a list should
        still be found
        """
        sac_path = "a[0]"
        sac_value = 1
        test_json = { "a[1]": 1 }
        expected_result = { 'found': True }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_different_key(self):
        """The SAC value is found in the SOT, but uses a different key"""
        sac_path = "a"
        sac_value = 1
        test_json = { "b": 1 }
        expected_result = {
            'found': True,
            'found_with_different_key': True,
            'sac_field': 'a',
            'audit_path': 'b',
            'value': 1,
        }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_different_key_bool(self):
        """Booleans should not be used to match fields"""
        sac_path = "a"
        sac_value = True
        test_json = { "b": True }
        expected_result = {
            'found': False,
        }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_bool_comparison(self):
        """Zeroes should not be used to match fields"""
        sac_path = "a"
        sac_value = 0
        test_json = { "b": 0 }
        expected_result = {
            'found': False,
        }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)

    def test_format_error(self):
        """Should not prematurely match on a similar value in another format"""
        sac_path = "a"
        sac_value = 1
        test_json = { "x": "01", "a": 1 }
        expected_result = { 'found': True }
        result = value_exists_in_audit(sac_path, sac_value, test_json)
        self.assertDictEqual(result, expected_result)


class TestCompareValues(TestCase):
    """Tests for other_formats_match"""
    def test_simple_equal(self):
        value_1 = 1
        value_2 = 1
        expected_result = { "found": False }
        result = other_formats_match(value_1, value_2)
        self.assertDictEqual(result, expected_result)

    def test_simple_not_equal(self):
        value_1 = 1
        value_2 = 2
        expected_result = { "found": False }
        result = other_formats_match(value_1, value_2)
        self.assertDictEqual(result, expected_result)

    def test_simple_zero(self):
        value_1 = 0
        value_2 = "0"
        expected_result = { "found": False }
        result = other_formats_match(value_1, value_2)
        self.assertDictEqual(result, expected_result)

    def test_int_str_1(self):
        value_1 = 1
        value_2 = "1"
        result = other_formats_match(value_1, value_2)
        self.assertTrue(result)

    def test_int_str_2(self):
        value_1 = "1"
        value_2 = 1
        result = other_formats_match(value_1, value_2)
        self.assertTrue(result)

    def test_list_1(self):
        value_1 = [1, 2]
        value_2 = 1
        result = other_formats_match(value_1, value_2)
        self.assertTrue(result)

    def test_list_2(self):
        value_1 = 1
        value_2 = [1, 2]
        result = other_formats_match(value_1, value_2)
        self.assertTrue(result)

    def test_dict_1(self):
        value_1 = { "a": 1 }
        value_2 = 1
        result = other_formats_match(value_1, value_2)
        self.assertTrue(result)

    def test_dict_2(self):
        value_1 = 1
        value_2 = { "a": 1 }
        result = other_formats_match(value_1, value_2)
        self.assertTrue(result)

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
            {'field': 'data_source', 'sac_value': 'foo', 'audit_value': 'GSAFAC'},
        )
        self.assertFalse(result[0])

    def test_json_valid(self):
        """Simple valid case for a JSON field"""
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': 1 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_json_invalid(self):
        """Generate a difference when a value differs between SAC and SOT"""
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': 2 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {'field': 'general_information', 'sac_path': 'a', 'sac_value': 2, 'error': 'Value from SAC.general_information.a not found in Audit'},
        )
        self.assertFalse(result[0])

    def test_json_audit_none_invalid(self):
        """
        Generate a difference when a field is empty in SAC, but not in
        SOT
        """
        audit = baker.make(Audit, version=0)
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': 1 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {'field': 'general_information', 'error': 'Field is empty in Audit, but not in SAC', 'sac_value': {'a': 1}, 'audit_value': None},
        )
        self.assertFalse(result[0])

    def test_json_sac_none_invalid(self):
        """
        Generate a difference when a field is empty in SOT, but not in
        SAC
        """
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        baker.make(SingleAuditChecklist, report_id=audit.report_id)
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {'field': 'general_information', 'error': 'Field is empty in SAC, but not in Audit', 'sac_value': None, 'audit_value': {'a': 1}},
        )
        self.assertFalse(result[0])

    def test_normalizing_keys(self):
        """Generate a difference when keys differ only by snake/kebab casing"""
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'foo_bar': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'foo-bar': 1 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {'field': 'general_information', 'sac_path': 'foo-bar', 'sac_value': 1, 'audit_path': 'general_information.foo_bar', 'error': 'Value from SAC.general_information.foo-bar found in Audit but with different structure/key'},
        )
        self.assertFalse(result[0])

    def test_json_different_formats_invalid(self):
        """Generate a difference when matching fields have different formats"""
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': '1' }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {'field': 'general_information', 'sac_path': 'a', 'sac_value': '1', 'found_with_different_format': True, 'found': True, 'error': '1 is int/float, found 1 as string'},
        )
        self.assertFalse(result[0])

    def test_format_error(self):
        """
        Don't prematurely match on values of different formats when a key
        match exists
        """
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'x': '01', 'a': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': 1 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_has_tribal_data_consent(self):
        """Valid case when tribal data consent exists"""
        audit = baker.make(Audit, version=0)
        audit.organization_type = 'tribal'
        audit.audit = { "tribal_data_consent": { 'foo': 'bar' } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.tribal_data_consent = { 'foo': 'bar' }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_no_tribal_data_consent(self):
        """Valid case when tribal data consent doesn't exist"""
        audit = baker.make(Audit, version=0)
        audit.organization_type = 'non-tribal'
        audit.audit = { "tribal_data_consent": {} }
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
        audit.audit = { 'federal_awards' : { 'foo': 'bar' } }
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.federal_awards = { 'Meta': { 'section_name': 'FederalAwardsExpended' } }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_findings_text(self):
        """Valid case for findings_text"""
        audit = baker.make(Audit, version=0)
        audit.audit = { 'findings_text' : [{ 'foo': 'bar' }] }
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.findings_text = {
            'FindingsText': {
                'findings_text_entries': [{
                    'foo': 'bar',
                }],
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
            'FindingsText': {},
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_corrective_action_plan(self):
        """Valid case for corrective_action_plan"""
        audit = baker.make(Audit, version=0)
        audit.audit = { 'corrective_action_plan' : [{ 'foo': 'bar' }] }
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.corrective_action_plan = {
            'CorrectiveActionPlan': {
                'corrective_action_plan_entries': [{
                    'foo': 'bar',
                }],
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
            'CorrectiveActionPlan': {},
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_eins(self):
        audit = baker.make(Audit, version=0)
        audit.audit = { "additional_eins": ["42"] }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.additional_eins = {
            "AdditionalEINs": {
                "additional_eins_entries": [
                    {
                        "additional_ein": "42"
                    }
                ]
            }
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertEqual(result[1], [])
        self.assertTrue(result[0])

    def test_eins_invalid(self):
        audit = baker.make(Audit, version=0)
        audit.audit = { "additional_eins": ["42"] }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.additional_eins = {
            "AdditionalEINs": {
                "additional_eins_entries": [
                    {
                        "additional_ein": "0"
                    }
                ]
            }
        }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertDictEqual(
            result[1][0],
            {'field': 'additional_eins', 'sac_value': ['0'], 'audit_value': ['42'], 'error': "EIN values don't match between SAC and Audit"},
        )
        self.assertFalse(result[0])
