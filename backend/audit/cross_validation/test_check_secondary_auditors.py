from django.test import TestCase
from model_bakery import baker
from audit.models import SingleAuditChecklist

from .check_secondary_auditors import check_secondary_auditors
from .errors import (
    err_secondary_auditors_empty,
    err_secondary_auditors_not_empty,
)
from .sac_validation_shape import sac_validation_shape

ERROR_EMPTY = {"error": err_secondary_auditors_empty()}
ERROR_PRESENT = {"error": err_secondary_auditors_not_empty()}


class CheckSecondaryAuditorsTests(TestCase):
    """
    General Information asks if there are secondary auditors; this answer needs to be
    consistent with the Secondary Auditors section.
    """

    def setUp(self):
        """
        Runs automatically on test start.
        Creates a SAC with a default secondary auditors response of "no".
        """
        self.sac = baker.make(SingleAuditChecklist)
        self.sac.general_information = {"secondary_auditors_exist": False}
        self.sac.secondary_auditors = {"SecondaryAuditors": {}}

    def validate_audit(self):
        """
        Validate the shaped SAC, return the result.
        """
        shaped_sac = sac_validation_shape(self.sac)
        return check_secondary_auditors(shaped_sac)

    def test_flag_sec_auds_no_sec_audits_no(self):
        """
        For a SAC with a no answer and no secondary auditors, there should be no errors.
        """
        validation_result = self.validate_audit()

        self.assertEqual(validation_result, [])

    def test_flag_sec_auds_no_sec_audits_yes(self):
        """
        For a SAC with a no answer that contains secondary auditors, there should be an error.
        """
        self.sac.secondary_auditors = {
            "SecondaryAuditors": {
                "secondary_auditors_entries": [{"secondary_auditor_name": "abcdefg"}],
            }
        }
        validation_result = self.validate_audit()
        self.assertEqual(validation_result, [ERROR_PRESENT])
    
    def test_flag_sec_auds_yes_sec_audits_no(self):
        """
        For a SAC with a yes answer and no secondary auditors, there should be an error.
        """
        self.sac.general_information = {"secondary_auditors_exist": True}
        validation_result = self.validate_audit()
        self.assertEqual(validation_result, [ERROR_EMPTY])
    
    def test_flag_sec_auds_yes_sec_audits_yes(self):
        """
        For a SAC with a yes answer and secondary auditors, there should be no errors.
        """
        self.sac.general_information = {"secondary_auditors_exist": True}
        self.sac.secondary_auditors = {
            "SecondaryAuditors": {
                "secondary_auditors_entries": [{"secondary_auditor_name": "abcdefg"}],
            }
        }
        validation_result = self.validate_audit()
        self.assertEqual(validation_result, [])
