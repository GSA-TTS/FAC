from django.test import TestCase
from model_bakery import baker
from audit.models import SingleAuditChecklist

from .errors import err_biennial_low_risk
from .check_biennial_low_risk import check_biennial_low_risk
from .sac_validation_shape import sac_validation_shape


class CheckBiennialLowRiskTests(TestCase):
    """
    Tests for check_biennial_low_risk validation
    """

    def test_no_biennial_no_low_risk(self):
        """
        Non-biennial and non-low-risk should validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "annual"}
        sac.audit_information = {"is_low_risk_auditee": False}

        validation_result = check_biennial_low_risk(sac_validation_shape(sac))

        self.assertEqual(validation_result, [])

    def test_biennial_no_low_risk(self):
        """
        Biennial and non-low-risk should validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "biennial"}
        sac.audit_information = {"is_low_risk_auditee": False}

        validation_result = check_biennial_low_risk(sac_validation_shape(sac))

        self.assertEqual(validation_result, [])

    def test_no_biennial_low_risk(self):
        """
        Non-biennial and low-risk should validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "annual"}
        sac.audit_information = {"is_low_risk_auditee": True}

        validation_result = check_biennial_low_risk(sac_validation_shape(sac))

        self.assertEqual(validation_result, [])

    def test_biennial_low_risk(self):
        """
        Biennial and low-risk should NOT validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"audit_period_covered": "biennial"}
        sac.audit_information = {"is_low_risk_auditee": True}

        validation_result = check_biennial_low_risk(sac_validation_shape(sac))

        self.assertEqual(len(validation_result), 1)
        self.assertEqual(validation_result[0], {"error": err_biennial_low_risk()})
