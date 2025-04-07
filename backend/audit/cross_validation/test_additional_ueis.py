from django.test import TestCase
from model_bakery import baker
from audit.models import Audit

from .additional_ueis import additional_ueis
from .audit_validation_shape import audit_validation_shape
from .errors import (
    err_additional_ueis_empty,
    err_additional_ueis_has_auditee_uei,
    err_additional_ueis_not_empty,
)

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
        audit_data = {"general_information": {"multiple_ueis_covered": False}}
        audit = baker.make(Audit, version=0, audit=audit_data)

        shaped_audit = audit_validation_shape(audit)
        validation_result = additional_ueis(shaped_audit)

        self.assertEqual(validation_result, [])

    def test_general_information_no_addl_ueis_ueis_present(self):
        """
        For a SAC with General Information and a no answer, there should be no
        additonal UEIs in that section.
        "No" answer plus data in section: invalid
        """
        audit_data = {
            "general_information": {"multiple_ueis_covered": False},
            "additional_ueis": ["987654321"],
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        shaped_audit = audit_validation_shape(audit)
        validation_result = additional_ueis(shaped_audit)

        self.assertEqual(validation_result, [ERROR_PRESENT])

    def test_general_information_addl_ueis_no_addl_ueis_section(self):
        """
        For a SAC with General Information and a yes answer, and no Additional UEIs
        data, generate errors.
        """
        audit_data = {"general_information": {"multiple_ueis_covered": True}}
        audit = baker.make(Audit, version=0, audit=audit_data)

        shaped_audit = audit_validation_shape(audit)
        validation_result = additional_ueis(shaped_audit)

        self.assertEqual(validation_result, [ERROR_EMPTY])

    def test_general_information_addl_ueis_no_addl_ueis_in_section(self):
        """
        For a SAC with General Information and a yes answer, and no Additional UEIs
        listed in the data, generate errors.
        """
        audit_data = {
            "general_information": {"multiple_ueis_covered": True},
            "additional_ueis": [],
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        shaped_audit = audit_validation_shape(audit)
        validation_result = additional_ueis(shaped_audit)

        self.assertEqual(validation_result, [ERROR_EMPTY])

    def test_general_information_addl_ueis_addl_ueis_in_section(self):
        """
        For a SAC with General Information and a yes answer, and Additional UEIs
        listed in the data, do not generate errors.
        """
        audit_data = {
            "general_information": {"multiple_ueis_covered": True},
            "additional_ueis": ["987654321"],
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        shaped_audit = audit_validation_shape(audit)
        validation_result = additional_ueis(shaped_audit)

        self.assertEqual(validation_result, [])

    def test_auditee_ueis_in_addl_ueis(self):
        """
        For a SAC with General Information and a yes answer, if the auditee_uei is
        found in the additonal_ueis, generate an error.
        """
        audit_data = {
            "general_information": {
                "auditee_uei": "123456789",
                "multiple_ueis_covered": True,
            },
            "additional_ueis": ["987654321", "123456789"],
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        shaped_audit = audit_validation_shape(audit)
        validation_result = additional_ueis(shaped_audit)

        self.assertEqual(validation_result, [ERROR_AUEI])
