from django.test import TestCase

from audit.models import SingleAuditChecklist

from .auditee_ueis_match import auditee_ueis_match
from .sac_validation_shape import sac_validation_shape

from model_bakery import baker


class AuditeeUEIsMatchTests(TestCase):
    def test_all_sections_none(self):
        """For a SAC with all sections empty, the auditee UEIs match"""
        sac = baker.make(SingleAuditChecklist)

        shaped_sac = sac_validation_shape(sac)

        validation_result = auditee_ueis_match(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_single_auditee_uei(self):
        """For a SAC with a single section, the auditee UEIs match"""
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {"auditee_uei": "123456789"}

        shaped_sac = sac_validation_shape(sac)

        validation_result = auditee_ueis_match(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_multiple_matching_auditee_ueis(self):
        """For a SAC with multiple sections where all auditee UEIs match, there should be no errors"""
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {"auditee_uei": "123456789"}
        sac.federal_awards = {"FederalAwards": {"auditee_uei": "123456789"}}

        shaped_sac = sac_validation_shape(sac)

        validation_result = auditee_ueis_match(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_multiple_mismatched_auditee_ueis(self):
        """For a SAC with multiple sections where there are mismatched auditee UEIs, there should be an error"""
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {"auditee_uei": "123456789"}
        sac.federal_awards = {"FederalAwards": {"auditee_uei": "123456780"}}

        shaped_sac = sac_validation_shape(sac)

        validation_result = auditee_ueis_match(shaped_sac)

        self.assertEqual(
            validation_result, [{"error": "Not all auditee UEIs matched."}]
        )
