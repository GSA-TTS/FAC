from django.test import TestCase

from audit.models import Audit
from .audit_validation_shape import audit_validation_shape

from .auditee_ueis_match import auditee_ueis_match

from model_bakery import baker


class AuditeeUEIsMatchTests(TestCase):
    def test_all_sections_none(self):
        """For a SAC with all sections empty, the auditee UEIs match"""
        audit = baker.make(Audit, version=0)

        shaped_audit = audit_validation_shape(audit)

        validation_result = auditee_ueis_match(shaped_audit)

        self.assertEqual(validation_result, [])

    def test_single_auditee_uei(self):
        """For a SAC with a single section, the auditee UEIs match"""
        audit_data = {"general_information": {"auditee_uei": "123456789"}}
        audit = baker.make(Audit, version=0, audit=audit_data)

        shaped_audit = audit_validation_shape(audit)

        validation_result = auditee_ueis_match(shaped_audit)

        self.assertEqual(validation_result, [])
