from django.test import TestCase
from model_bakery import baker
from audit.models import SingleAuditChecklist

from .errors import err_biennial_low_risk
from .validate_general_information import _check_biennial_low_risk


class CheckBiennialLowRiskTests(TestCase):
    """
    Tests for _check_biennial_low_risk validation
    """

    def test_no_biennial_no_low_risk(self):
        """
        Non-biennial and non-low-risk should validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "annual"}
        sac.audit_information = {"is_low_risk_auditee": False}

        validation_result = _check_biennial_low_risk(
            sac.general_information, sac.audit_information
        )

        self.assertEqual(validation_result, [])

    def test_biennial_no_low_risk(self):
        """
        Biennial and non-low-risk should validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "biennial"}
        sac.audit_information = {"is_low_risk_auditee": False}

        validation_result = _check_biennial_low_risk(
            sac.general_information, sac.audit_information
        )

        self.assertEqual(validation_result, [])

    def test_no_biennial_low_risk(self):
        """
        Non-biennial and low-risk should validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "annual"}
        sac.audit_information = {"is_low_risk_auditee": True}

        validation_result = _check_biennial_low_risk(
            sac.general_information, sac.audit_information
        )

        self.assertEqual(validation_result, [])

    def test_biennial_low_risk(self):
        """
        Biennial and low-risk should NOT validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "biennial"}
        sac.audit_information = {"is_low_risk_auditee": True}

        validation_result = _check_biennial_low_risk(
            sac.general_information, sac.audit_information
        )

        self.assertEqual(len(validation_result), 1)
        self.assertEqual(validation_result[0], {"error": err_biennial_low_risk})
