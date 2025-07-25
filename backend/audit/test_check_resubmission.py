from django.test import TestCase
from django.utils import timezone
from audit.models import SingleAuditChecklist
from audit.check_resubmission_allowed import check_resubmission_allowed


def create_sac(
    *,
    submitted_by=None,
    status="IN_PROGRESS",
    version=1,
    meta=None,
    uei="TESTUEI123",
    audit_year=2023,
    transition_date=None,
):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = submitted_by or User.objects.get_or_create(username="testuser")[0]

    return SingleAuditChecklist.objects.create(
        submitted_by=user,
        submission_status=status,
        general_information={
            "auditee_fiscal_period_end": timezone.now().date().isoformat(),
            "uei": uei,
            "audit_year": audit_year,
            "version": version,
        },
        resubmission_meta=meta,
        transition_name=[status],
        transition_date=[transition_date or timezone.now()],
    )


class TestCheckResubmissionAllowed(TestCase):

    def test_deprecated_audit_not_allowed(self):
        sac = create_sac(
            version=2,
            meta={"resubmission_status": "DEPRECATED_VIA_RESUBMISSION"},
        )
        allowed, message = check_resubmission_allowed(sac)
        self.assertFalse(allowed)
        self.assertIn("deprecated", message.lower())

    def test_original_submission_v1_allowed(self):
        sac = create_sac(
            version=1,
            meta={"resubmission_status": "ORIGINAL_SUBMISSION"},
        )
        allowed, message = check_resubmission_allowed(sac)
        self.assertTrue(allowed)
        self.assertIn("eligible", message.lower())

    def test_most_recent_v2_allowed(self):
        sac = create_sac(
            version=2,
            meta={"resubmission_status": "MOST_RECENT"},
        )
        allowed, message = check_resubmission_allowed(sac)
        self.assertTrue(allowed)
        self.assertIn("eligible", message.lower())

    def test_legacy_single_record_allowed(self):
        sac = create_sac(version=0, meta=None)
        allowed, message = check_resubmission_allowed(sac)
        self.assertTrue(allowed)
        self.assertIn("legacy", message.lower())

    def test_legacy_multiple_records_not_most_recent(self):
        earlier = create_sac(
            version=0,
            meta=None,
            transition_date=timezone.now() - timezone.timedelta(seconds=20),
        )
        allowed, message = check_resubmission_allowed(earlier)
        self.assertFalse(allowed)
        self.assertIn("most recent", message.lower())

    def test_legacy_multiple_records_most_recent_allowed(self):
        create_sac(
            version=0,
            meta=None,
            transition_date=timezone.now() - timezone.timedelta(seconds=20),
        )
        latest = create_sac(version=0, meta=None, transition_date=timezone.now())
        allowed, message = check_resubmission_allowed(latest)
        self.assertTrue(allowed)
        self.assertIn("eligible", message.lower())

    def test_legacy_suspicious_timestamp_cluster(self):
        ts_base = timezone.now()
        sac2 = create_sac(
            version=0,
            meta=None,
            transition_date=ts_base + timezone.timedelta(seconds=5),
        )
        allowed, message = check_resubmission_allowed(sac2)
        self.assertFalse(allowed)
        self.assertIn("timestamps", message.lower())
