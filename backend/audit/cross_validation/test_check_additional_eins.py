from django.test import TestCase
from model_bakery import baker
from audit.models import SingleAuditChecklist

from .check_additional_eins import check_additional_eins
from .errors import (
    err_additional_eins_empty,
    err_additional_eins_has_auditee_ein,
    err_additional_eins_not_empty,
)
from .sac_validation_shape import sac_validation_shape

ERROR_EMPTY = {"error": err_additional_eins_empty()}
ERROR_PRESENT = {"error": err_additional_eins_not_empty()}
ERROR_AEIN = {"error": err_additional_eins_has_auditee_ein()}


class CheckAdditionalEINsTests(TestCase):
    """
    General Information asks if there are additional EINs; this answer needs to be
    consistent with the Additional EINs section.

    Note: This class is essentially a copy of its UEI counterpart. When updating one, it is likely appropriate to update the other.
    """

    def test_general_information_no_addl_eins(self):
        """
        For a SAC with General Information and a no answer, there should be no
        additonal EINs in that section. "No" answer plus no section = valid.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_eins_covered": False}

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_additional_eins(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_general_information_no_addl_eins_eins_present(self):
        """
        For a SAC with General Information and a no answer, there should be no
        additonal EINs in that section.
        "No" answer plus data in section: invalid
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_eins_covered": False}
        sac.additional_eins = {
            "AdditionalEINs": {
                "auditee_ein": "123456789",
                "additional_eins_entries": [{"additional_ein": "987654321"}],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_additional_eins(shaped_sac)

        self.assertEqual(validation_result, [ERROR_PRESENT])

    def test_general_information_addl_eins_no_addl_eins_section(self):
        """
        For a SAC with General Information and a yes answer, and no Additional EINs
        data, generate errors.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_eins_covered": True}

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_additional_eins(shaped_sac)

        self.assertEqual(validation_result, [ERROR_EMPTY])

    def test_general_information_addl_eins_no_addl_eins_in_section(self):
        """
        For a SAC with General Information and a yes answer, and no Additional EINs
        listed in the data, generate errors.
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {"multiple_eins_covered": True}
        sac.additional_eins = {}

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_additional_eins(shaped_sac)

        self.assertEqual(validation_result, [ERROR_EMPTY])

        sac.additional_eins = {
            "AdditionalEINs": {
                "auditee_ein": "123456789",
                "additional_eins_entries": [],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_additional_eins(shaped_sac)

        self.assertEqual(validation_result, [ERROR_EMPTY])

    def test_general_information_addl_eins_addl_eins_in_section(self):
        """
        For a SAC with General Information and a yes answer, and Additional EINs
        listed in the data, do not generate errors.
        """
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {"multiple_eins_covered": True}
        sac.additional_eins = {
            "AdditionalEINs": {
                "auditee_ein": "123456789",
                "additional_eins_entries": [{"additional_ein": "987654321"}],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_additional_eins(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_auditee_eins_in_addl_eins(self):
        """
        For a SAC with General Information and a yes answer, if the auditee_ein is
        found in the additonal_eins, generate an error.
        """
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {
            "auditee_ein": "123456789",
            "multiple_eins_covered": True,
        }
        sac.additional_eins = {
            "AdditionalEINs": {
                "auditee_ein": "123456789",
                "additional_eins_entries": [
                    {"additional_ein": "987654321"},
                    {"additional_ein": "123456789"},
                ],
            }
        }

        shaped_sac = sac_validation_shape(sac)
        validation_result = check_additional_eins(shaped_sac)

        self.assertEqual(validation_result, [ERROR_AEIN])
