from django.test import TestCase
from django.utils import timezone

from datetime import datetime, timezone as dt_timezone
from model_bakery import baker

from audit.models import SingleAuditChecklist
from audit.models.constants import STATUS, RESUBMISSION_STATUS
from audit.check_resubmission_allowed import (
    check_resubmission_allowed,
    get_last_transition_date,
)
from dissemination.models import General


def create_sac(
    *,
    submitted_by=None,
    meta=None,
    version=2,
    status=STATUS.IN_PROGRESS,
    transition_date=None,
    general_information=None,
):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = submitted_by or User.objects.get_or_create(username="testuser")[0]

    if general_information is None:
        general_information = {
            "auditee_uei": "TESTUEI123",
            "auditee_fiscal_period_end": timezone.now().date().isoformat(),
        }

    if meta is not None and "version" not in meta:
        meta["version"] = version

    sac = SingleAuditChecklist.objects.create(
        submitted_by=user,
        submission_status=status,
        general_information=general_information,
        transition_name=[status],
    )

    # The SAC's corresponding General entry also created
    baker.make(
        General,
        report_id=sac.report_id,
        auditee_uei=general_information["auditee_uei"],
        audit_year=general_information["auditee_fiscal_period_end"].split("-")[0],
    )

    if meta is not None:
        sac.resubmission_meta = meta

    sac.version = version

    if transition_date:
        sac.transition_date = [transition_date]
        sac.save(update_fields=["transition_date", "version"])
    else:
        sac.save(update_fields=["version"])

    return sac


class TestCheckResubmissionAllowed(TestCase):

    def test_get_last_transition_date_handles_missing_dates(self):
        sac = SingleAuditChecklist()
        sac.transition_date = None
        date = get_last_transition_date(sac)
        self.assertEqual(date, datetime.min.replace(tzinfo=dt_timezone.utc))

    def test_deprecated_audit_not_allowed(self):
        sac = create_sac(
            version=2,
            meta={"resubmission_status": RESUBMISSION_STATUS.DEPRECATED, "version": 2},
            status=STATUS.DISSEMINATED,
        )
        allowed, message = check_resubmission_allowed(sac)
        self.assertFalse(allowed)
        self.assertIn("deprecated", message.lower())

    def test_most_recent_v2_allowed(self):
        sac = create_sac(
            version=2,
            meta={"resubmission_status": RESUBMISSION_STATUS.MOST_RECENT},
            status=STATUS.DISSEMINATED,
        )
        allowed, message = check_resubmission_allowed(sac)
        self.assertTrue(allowed)
        self.assertIn("eligible", message.lower())

    def test_legacy_single_record_allowed(self):
        sac = create_sac(
            meta=None,
            status=STATUS.DISSEMINATED,
            general_information={
                "auditee_uei": "TESTUEI1",
                "auditee_fiscal_period_end": timezone.now().date().isoformat(),
            },
        )
        sac.save()  # ensure sac.id is set
        allowed, message = check_resubmission_allowed(sac)
        self.assertTrue(allowed)
        self.assertIn("legacy", message.lower())

    def test_legacy_multiple_records_not_most_recent(self):
        shared_info = {
            "auditee_uei": "TESTUEI1",
            "auditee_fiscal_period_end": timezone.now().date().isoformat(),
        }

        # Most recent
        create_sac(
            meta=None,
            status=STATUS.DISSEMINATED,
            general_information=shared_info,
            transition_date=timezone.now(),
        )

        # Older
        earlier = create_sac(
            meta=None,
            status=STATUS.DISSEMINATED,
            general_information=shared_info,
            transition_date=timezone.now() - timezone.timedelta(seconds=30),
        )

        earlier.save()  # must have an ID
        allowed, message = check_resubmission_allowed(earlier)
        self.assertFalse(allowed)
        self.assertIn("most recent", message.lower())

    def test_legacy_multiple_records_most_recent_allowed(self):
        shared_info = {
            "auditee_uei": "TESTUEI1",
            "auditee_fiscal_period_end": timezone.now().date().isoformat(),
        }

        # Older
        create_sac(
            meta=None,
            status=STATUS.DISSEMINATED,
            general_information=shared_info,
            transition_date=timezone.now() - timezone.timedelta(seconds=20),
        )

        # Most recent
        latest = create_sac(
            version=0,
            meta=None,
            status=STATUS.DISSEMINATED,
            general_information=shared_info,
            transition_date=timezone.now(),
        )
        latest.save()
        allowed, message = check_resubmission_allowed(latest)
        self.assertTrue(allowed)
        self.assertIn("eligible", message.lower())

    def test_legacy_suspicious_timestamp_cluster(self):
        ts_base = timezone.now()

        create_sac(
            meta=None,
            status=STATUS.DISSEMINATED,
            transition_date=ts_base,
        )
        sac2 = create_sac(
            meta=None,
            status=STATUS.DISSEMINATED,
            transition_date=ts_base + timezone.timedelta(seconds=5),
        )

        # sac2 is the most recent but fails timestamps proximity (<10s)
        allowed, message = check_resubmission_allowed(sac2)
        self.assertFalse(allowed)
        self.assertIn("timestamps", message.lower())

    def test_resubmission_blocked_when_status_not_disseminated(self):
        sac = create_sac(
            version=2,
            meta={"resubmission_status": RESUBMISSION_STATUS.MOST_RECENT},
            status=STATUS.CERTIFIED,
        )
        allowed, message = check_resubmission_allowed(sac)
        self.assertFalse(allowed)
        self.assertIn("disseminated", message.lower())
        self.assertIn("current status", message.lower())

    def test_resubmission_blocked_when_status_is_none(self):
        sac = SingleAuditChecklist(
            general_information={
                "auditee_uei": "TESTUEI123",
                "auditee_fiscal_period_end": timezone.now().date().isoformat(),
            },
            resubmission_meta={"version": 2, "resubmission_status": "most_recent"},
            # don't set submission_status
        )
        allowed, msg = check_resubmission_allowed(sac)
        self.assertFalse(allowed)
        self.assertIn("Resubmission is only allowed", msg)
