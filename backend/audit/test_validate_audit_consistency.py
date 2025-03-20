from django.test import TestCase
from model_bakery import baker

from audit.models import Audit, SingleAuditChecklist
from audit.models.utils import (
  flatten_json,
  value_exists_in_audit,
  compare_values,
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

class TestCompareValues(TestCase):
    """Tests for compare_values"""
    def test_simple_false(self):
        value_1 = 1
        value_2 = 2
        expected_result = { "found": False }
        result = compare_values(value_1, value_2)
        self.assertDictEqual(result, expected_result)

    # int/float is not an option, only if one is str
    # def test_float_1(self):
    #     value_1 = 1.0
    #     value_2 = 1
    #     result = compare_values(value_1, value_2)
    #     self.assertTrue(result)

    # def test_float_2(self):
    #     value_1 = 1
    #     value_2 = 1.0
    #     result = compare_values(value_1, value_2)
    #     self.assertTrue(result)

    def test_int_str_1(self):
        value_1 = 1
        value_2 = "1"
        result = compare_values(value_1, value_2)
        self.assertTrue(result)

    def test_int_str_2(self):
        value_1 = "1"
        value_2 = 1
        result = compare_values(value_1, value_2)
        self.assertTrue(result)

    # Are these possible, since we're flattening?
    def test_list_1(self):
        value_1 = [1, 2]
        value_2 = 1
        result = compare_values(value_1, value_2)
        self.assertTrue(result)

    def test_list_2(self):
        value_1 = 1
        value_2 = [1, 2]
        result = compare_values(value_1, value_2)
        self.assertTrue(result)

    def test_dict_1(self):
        value_1 = { "a": 1 }
        value_2 = 1
        result = compare_values(value_1, value_2)
        self.assertTrue(result)

    def test_dict_2(self):
        value_1 = 1
        value_2 = { "a": 1 }
        result = compare_values(value_1, value_2)
        self.assertTrue(result)

class TestValidateAuditConsistency(TestCase):
    """Tests for validate_audit_consistency"""
    def test_simple_valid(self):
        audit = baker.make(Audit, version=0)
        baker.make(SingleAuditChecklist, report_id=audit.report_id)
        result = validate_audit_consistency(audit)
        self.assertTrue(result[0])
        self.assertEqual(result[1], [])

    def test_simple_invalid(self):
        audit = baker.make(Audit, version=0)
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.data_source = "foo"
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertFalse(result[0])
        self.assertEqual(result[1], [{'field': 'data_source', 'sac_value': 'foo', 'audit_value': 'GSAFAC'}])

    def test_json_valid(self):
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': 1 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertTrue(result[0])
        self.assertEqual(result[1], [])

    def test_json_invalid(self):
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': 2 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertFalse(result[0])
        self.assertEqual(
            result[1],
            [{'field': 'general_information', 'sac_path': 'a', 'sac_value': 2, 'error': 'Value from SAC.general_information.a not found in Audit'}],
        )

    def test_json_audit_none_invalid(self):
        audit = baker.make(Audit, version=0)
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': 1 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertFalse(result[0])
        self.assertEqual(
            result[1],
            [{'field': 'general_information', 'error': 'Field is empty in Audit, but not in SAC', 'sac_value': {'a': 1}, 'audit_value': None}],
        )

    def test_json_sac_none_invalid(self):
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        baker.make(SingleAuditChecklist, report_id=audit.report_id)
        result = validate_audit_consistency(audit)
        self.assertFalse(result[0])
        self.assertEqual(
            result[1],
            [{'field': 'general_information', 'error': 'Field is empty in SAC, but not in Audit', 'sac_value': None, 'audit_value': {'a': 1}}],
        )

    def test_normalizing_keys(self):
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'foo_bar': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'foo-bar': 1 }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertFalse(result[0])
        self.assertEqual(
            result[1],
            [{'field': 'general_information', 'sac_path': 'foo-bar', 'sac_value': 1, 'audit_path': 'general_information.foo_bar', 'error': 'Value from SAC.general_information.foo-bar found in Audit but with different structure/key'}],
        )

    def test_json_different_formats_invalid(self):
        audit = baker.make(Audit, version=0)
        audit.audit = { 'general_information': { 'a': 1 } }
        audit.save()
        sac = baker.make(SingleAuditChecklist, report_id=audit.report_id)
        sac.general_information = { 'a': '1' }
        sac.save()
        result = validate_audit_consistency(audit)
        self.assertFalse(result[0])
        self.assertEqual(
            result[1],
            [{'field': 'general_information', 'sac_path': 'a', 'sac_value': '1', 'found_with_different_format': True, 'found': True, 'error': '1 is int/float, found 1 as string'}],
        )
