from django.test import TestCase
from model_bakery import baker
from audit.models import Audit
from .audit_validation_shape import audit_validation_shape

from .errors import err_biennial_low_risk
from .check_biennial_low_risk import check_biennial_low_risk


class CheckBiennialLowRiskTests(TestCase):
    """
    Tests for check_biennial_low_risk validation
    """

    def test_no_biennial_no_low_risk(self):
        """
        Non-biennial and non-low-risk should validate
        """
        audit_data = {
            "general_information": {"audit_period_covered": "annual"},
            "audit_information": {"is_low_risk_auditee": False},
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        validation_result = check_biennial_low_risk(audit_validation_shape(audit))

        self.assertEqual(validation_result, [])

    def test_biennial_no_low_risk(self):
        """
        Biennial and non-low-risk should validate
        """
        audit_data = {
            "general_information": {"audit_period_covered": "biennial"},
            "audit_information": {"is_low_risk_auditee": False},
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        validation_result = check_biennial_low_risk(audit_validation_shape(audit))

        self.assertEqual(validation_result, [])

    def test_no_biennial_low_risk(self):
        """
        Non-biennial and low-risk should validate
        """
        audit_data = {
            "general_information": {"audit_period_covered": "annual"},
            "audit_information": {"is_low_risk_auditee": True},
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        validation_result = check_biennial_low_risk(audit_validation_shape(audit))

        self.assertEqual(validation_result, [])

    def test_biennial_low_risk(self):
        """
        Biennial and low-risk should NOT validate
        """
        audit_data = {
            "general_information": {"audit_period_covered": "biennial"},
            "audit_information": {"is_low_risk_auditee": True},
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        validation_result = check_biennial_low_risk(audit_validation_shape(audit))

        self.assertEqual(len(validation_result), 1)
        self.assertEqual(validation_result[0], {"error": err_biennial_low_risk()})

    def test_empty_sections(self):
        """
        Empty general information/audit information sections should validate
        """
        audit_data_empty_gen_info = {
            "general_information": {},
            "audit_information": {"is_low_risk_auditee": True},
        }
        audit_empty_gen_info = baker.make(
            Audit, version=0, audit=audit_data_empty_gen_info
        )

        audit_data_empty_audit_info = {
            "general_information": {"audit_period_covered": "biennial"},
            "audit_information": {},
        }
        audit_empty_audit_info = baker.make(
            Audit, version=0, audit=audit_data_empty_audit_info
        )

        audit_empty = baker.make(Audit, version=0, audit={})

        validation_result_empty_gen = check_biennial_low_risk(
            audit_validation_shape(audit_empty_gen_info)
        )
        self.assertEqual(validation_result_empty_gen, [])

        validation_result_empty_audit = check_biennial_low_risk(
            audit_validation_shape(audit_empty_audit_info)
        )
        self.assertEqual(validation_result_empty_audit, [])

        validation_result_empty = check_biennial_low_risk(
            audit_validation_shape(audit_empty)
        )
        self.assertEqual(validation_result_empty, [])
