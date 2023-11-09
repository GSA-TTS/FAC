from django.test import TestCase
from model_bakery import baker
from audit.models import SingleAuditChecklist

from .additional_ueis import additional_ueis
from .errors import (
    err_additional_ueis_empty,
    err_additional_ueis_has_auditee_uei,
    err_additional_ueis_not_empty,
)
from .sac_validation_shape import sac_validation_shape

ERROR_EMPTY = {"error": err_additional_ueis_empty()}
ERROR_PRESENT = {"error": err_additional_ueis_not_empty()}
ERROR_AUEI = {"error": err_additional_ueis_has_auditee_uei()}


class AdditionalUEIsTests(TestCase):
    """
    General Information asks if there are additional UEIs; this answer needs to be
    consistent with the Additional UEIs section.
    """

    def test_general_information_no_addl_ueis(self):
        """
        For a SAC with General Information and a no answer, there should be no
        additonal UEIs in that section. "No" answer plus no section = valid.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_ueis_covered": False}

        shaped_sac = sac_validation_shape(sac)
        validation_result = additional_ueis(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_general_information_no_addl_ueis_ueis_present(self):
        """
        For a SAC with General Information and a no answer, there should be no
        additonal UEIs in that section.
        "No" answer plus data in section: invalid
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_ueis_covered": False}
        sac.additional_ueis = {
            "AdditionalUEIs": {
                "auditee_uei": "123456789",
                "additional_ueis_entries": [{"additional_uei": "987654321"}],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = additional_ueis(shaped_sac)

        self.assertEqual(validation_result, [ERROR_PRESENT])

    def test_general_information_addl_ueis_no_addl_ueis_section(self):
        """
        For a SAC with General Information and a yes answer, and no Additional UEIs
        data, generate errors.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_ueis_covered": True}

        shaped_sac = sac_validation_shape(sac)
        validation_result = additional_ueis(shaped_sac)

        self.assertEqual(validation_result, [ERROR_EMPTY])

    def test_general_information_addl_ueis_no_addl_ueis_in_section(self):
        """
        For a SAC with General Information and a yes answer, and no Additional UEIs
        listed in the data, generate errors.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_ueis_covered": True}
        sac.additional_ueis = {}

        shaped_sac = sac_validation_shape(sac)
        validation_result = additional_ueis(shaped_sac)

        self.assertEqual(validation_result, [ERROR_EMPTY])

        sac.additional_ueis = {
            "AdditionalUEIs": {
                "auditee_uei": "123456789",
                "additional_ueis_entries": [],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = additional_ueis(shaped_sac)

        self.assertEqual(validation_result, [ERROR_EMPTY])

    def test_general_information_addl_ueis_addl_ueis_in_section(self):
        """
        For a SAC with General Information and a yes answer, and Additional UEIs
        listed in the data, do not generate errors.
        """
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {"multiple_ueis_covered": True}
        sac.additional_ueis = {
            "AdditionalUEIs": {
                "auditee_uei": "123456789",
                "additional_ueis_entries": [{"additional_uei": "987654321"}],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = additional_ueis(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_auditee_ueis_in_addl_ueis(self):
        """
        For a SAC with General Information and a yes answer, if the auditee_uei is
        found in the additonal_ueis, generate an error.
        """
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {
            "auditee_uei": "123456789",
            "multiple_ueis_covered": True,
        }
        sac.additional_ueis = {
            "AdditionalUEIs": {
                "auditee_uei": "123456789",
                "additional_ueis_entries": [
                    {"additional_uei": "987654321"},
                    {"additional_uei": "123456789"},
                ],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = additional_ueis(shaped_sac)

        self.assertEqual(validation_result, [ERROR_AUEI])
