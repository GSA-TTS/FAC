from django.test import TestCase
from model_bakery import baker
from audit.models import SingleAuditChecklist

from .check_ein_attestations import check_ein_attestations
from .errors import (
    err_ein_attestation,
)
from .sac_validation_shape import sac_validation_shape

ERROR_AUDITEE_UNCHECKED = {"error": err_ein_attestation("ein_not_an_ssn_attestation")}
ERROR_AUDITOR_UNCHECKED = {
    "error": err_ein_attestation("auditor_ein_not_an_ssn_attestation")
}


class CheckEINAttestationsTests(TestCase):
    """
    General Information requires attestation that EIN values are not SSNs. They must be checked.
    """

    def test_general_information_ein_attestations_checked(self):
        """
        For a SAC with General Information with both EIN attestations checked, there should be no errors.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "ein_not_an_ssn_attestation": True,
            "auditor_ein_not_an_ssn_attestation": True,
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_ein_attestations(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_general_information_ein_attestations_one_unchecked(self):
        """
        For a SAC with General Information with either EIN attestation unchecked, there should be an error.
        """
        sac = baker.make(SingleAuditChecklist)
        auditee_unchecked = {
            "ein_not_an_ssn_attestation": False,
            "auditor_ein_not_an_ssn_attestation": True,
        }
        auditor_unchecked = {
            "ein_not_an_ssn_attestation": True,
            "auditor_ein_not_an_ssn_attestation": False,
        }

        # Only the auditee box is unchecked
        sac.general_information = auditee_unchecked
        shaped_sac = sac_validation_shape(sac)
        validation_result = check_ein_attestations(shaped_sac)
        self.assertEqual(validation_result, [ERROR_AUDITEE_UNCHECKED])

        # Only the auditor box is unchecked
        sac.general_information = auditor_unchecked
        shaped_sac = sac_validation_shape(sac)
        validation_result = check_ein_attestations(shaped_sac)
        self.assertEqual(validation_result, [ERROR_AUDITOR_UNCHECKED])

    def test_general_information_ein_attestations_both_unchecked(self):
        """
        For a SAC with General Information with both EIN attestations unchecked, there should be two errors.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "ein_not_an_ssn_attestation": False,
            "auditor_ein_not_an_ssn_attestation": False,
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_ein_attestations(shaped_sac)

        self.assertEqual(
            validation_result, [ERROR_AUDITEE_UNCHECKED, ERROR_AUDITOR_UNCHECKED]
        )
