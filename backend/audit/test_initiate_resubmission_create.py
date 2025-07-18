# audit/test_initiate_resubmission_create.py

from django.test import TestCase
from django.contrib.auth import get_user_model

from audit.models import SingleAuditChecklist
from audit.models.constants import STATUS
from audit.models import SubmissionEvent

User = get_user_model()


class ResubmissionTest(TestCase):
    def test_initiate_resubmission_creates_valid_copy(self):
        user_password = "test_password"  # nosec B106
        user = User.objects.create_user(username="testuser", password=user_password)

        general_info = {
            "auditee_fiscal_period_end": "2024-12-31",
            "uei": "TESTUEI123456",
        }

        orig = SingleAuditChecklist.objects.create(
            submitted_by=user,
            submission_status=STATUS.IN_PROGRESS,
            general_information=general_info,
        )

        resub = orig.initiate_resubmission(user=user, event_type="resubmission_started")

        # ✅ Report ID should follow the strict format
        self.assertRegex(resub.report_id, r"\d{4}-\d{2}-GSAFAC-\d{10}")

        # ✅ UEI and audit year match original
        self.assertEqual(
            resub.general_information["uei"], orig.general_information["uei"]
        )
        self.assertEqual(
            resub.general_information["auditee_fiscal_period_end"],
            orig.general_information["auditee_fiscal_period_end"],
        )

        # ✅ Submission status and transition state
        self.assertEqual(resub.submission_status, STATUS.IN_PROGRESS)
        self.assertEqual(resub.transition_name, [STATUS.IN_PROGRESS])

        # ✅ resubmission_meta is populated correctly
        self.assertEqual(resub.resubmission_meta["previous_report_id"], orig.report_id)
        self.assertEqual(resub.resubmission_meta["previous_row_id"], orig.id)
        self.assertIn(
            "MOST_RECENT_SUBMISSION", resub.resubmission_meta["resubmission_state"]
        )
        self.assertGreater(resub.resubmission_meta["version"], 1)

        # Confirm SubmissionEvent created
        self.assertTrue(
            SubmissionEvent.objects.filter(
                sac=resub, user=user, event="resubmission_started"
            ).exists()
        )
