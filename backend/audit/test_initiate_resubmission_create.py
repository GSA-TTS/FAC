# audit/test_initiate_resubmission_create.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from audit.models import SingleAuditChecklist, SubmissionEvent
from audit.models.constants import STATUS
from dissemination.models.general import ResubmissionStatus

User = get_user_model()


class ResubmissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="resubuser")
        self.general_info = {
            "auditee_fiscal_period_end": "2024-12-31",
            "uei": "TESTUEI999999",
        }
        self.orig = SingleAuditChecklist.objects.create(
            submitted_by=self.user,
            submission_status=STATUS.IN_PROGRESS,
            general_information=self.general_info,
        )

    def test_resubmission_is_created_atomically_and_correctly(self):
        resub = self.orig.initiate_resubmission(
            user=self.user, event_type=SubmissionEvent.EventType.RESUBMISSION_STARTED
        )

        # Report ID format check
        self.assertRegex(resub.report_id, r"\d{4}-\d{2}-GSAFAC-\d{10}")

        # Audit year and UEI match
        self.assertEqual(
            resub.general_information["uei"], self.orig.general_information["uei"]
        )
        self.assertEqual(
            resub.general_information["auditee_fiscal_period_end"],
            self.orig.general_information["auditee_fiscal_period_end"],
        )

        # Submission status and transition
        self.assertEqual(resub.submission_status, STATUS.IN_PROGRESS)
        self.assertEqual(resub.transition_name, [STATUS.IN_PROGRESS])

        # Resubmission meta structure
        self.assertEqual(
            resub.resubmission_meta["previous_report_id"], self.orig.report_id
        )
        self.assertEqual(resub.resubmission_meta["previous_row_id"], self.orig.id)
        self.assertEqual(
            resub.resubmission_meta["resubmission_status"],
            ResubmissionStatus.MOST_RECENT,
        )
        self.assertGreater(resub.resubmission_meta["version"], 1)

        # SubmissionEvent created on both SACs
        self.assertTrue(
            SubmissionEvent.objects.filter(
                sac=resub,
                user=self.user,
                event=SubmissionEvent.EventType.RESUBMISSION_STARTED,
            ).exists()
        )

        self.assertTrue(
            SubmissionEvent.objects.filter(
                sac=self.orig,
                user=self.user,
                event=SubmissionEvent.EventType.RESUBMISSION_INITIATED,
            ).exists()
        )

    def test_cannot_create_duplicate_resubmission(self):
        # First resubmission should succeed
        self.orig.initiate_resubmission(
            user=self.user, event_type=SubmissionEvent.EventType.RESUBMISSION_STARTED
        )

        # Second resubmission should raise ValidationError
        with self.assertRaises(ValidationError):
            self.orig.initiate_resubmission(
                user=self.user,
                event_type=SubmissionEvent.EventType.RESUBMISSION_INITIATED,
            )
