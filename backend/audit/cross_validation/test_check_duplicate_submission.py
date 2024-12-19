from datetime import date, timedelta
from model_bakery import baker

from django.test import TestCase
from django.utils import timezone as django_timezone

from audit.models import SingleAuditChecklist, ResubmissionWaiver
from dissemination.models import General

from .errors import err_duplicate_submission
from .check_duplicate_submission import check_duplicate_submission
from .sac_validation_shape import sac_validation_shape


class CheckDuplicateSubmissionTests(TestCase):
    """
    Tests for check_duplicate_submission validation
    """

    def test_empty_sections(self):
        """
        Empty general information sections should validate
        """
        sac_empty = baker.make(SingleAuditChecklist)
        sac_empty.general_information = {}

        validation_result_empty_gen = check_duplicate_submission(
            sac_validation_shape(sac_empty)
        )
        self.assertEqual(validation_result_empty_gen, [])

    def test_non_duplicate(self):
        """
        A non duplicate should always validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "auditee_fiscal_period_start": "2024-01-01",
            "auditee_uei": "SUPERC00LUE1",
        }

        # Create some disseminated audits that don't conflict, but have the same audit year or UEI.
        baker.make(General, audit_year="2024", auditee_uei="N0TUSEFULUE1")
        baker.make(General, audit_year="2022", auditee_uei="SUPERC00LUE1")

        validation_result = check_duplicate_submission(sac_validation_shape(sac))

        self.assertEqual(validation_result, [])

    def test_duplicate(self):
        """
        A duplicate should throw an error
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "auditee_fiscal_period_start": "2024-01-01",
            "auditee_uei": "0LDANDSADUE1",
        }

        # Create a disseminated audit that does conflict.
        baker.make(General, audit_year="2024", auditee_uei="0LDANDSADUE1")

        validation_result = check_duplicate_submission(sac_validation_shape(sac))

        self.assertEqual(validation_result, [{"error": err_duplicate_submission()}])

    def test_waived_duplicate(self):
        """
        A duplicate with a waiver should validate
        """
        sac = baker.make(SingleAuditChecklist)
        sac.general_information = {
            "auditee_fiscal_period_start": "2024-01-01",
            "auditee_uei": "0LDANDSADUE1",
        }

        # Create a disseminated audit that does conflict.
        baker.make(General, audit_year="2024", auditee_uei="0LDANDSADUE1")

        # Create a waiver
        one_month_from_today = django_timezone.now() + timedelta(days=30)
        baker.make(
            ResubmissionWaiver,
            audit_year="2024",
            uei="0LDANDSADUE1",
            expiration=one_month_from_today,
        )

        validation_result = check_duplicate_submission(sac_validation_shape(sac))

        self.assertEqual(validation_result, [{"error": err_duplicate_submission()}])
