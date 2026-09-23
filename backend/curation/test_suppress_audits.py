from copy import deepcopy
from typing import Any, Dict
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker

from audit.models import SingleAuditChecklist
from audit.models.constants import RESUBMISSION_STATUS, STATUS
from curation.curationlib.suppress_audits import (
    _flag_sac_for_administrative_removal,
    repair_resubmission_chain,
    suppress_audit,
)
from dissemination.models import AdditionalEin, FederalAward, General

SAC: Dict[str, Any] = {
    "report_id": "2022-42-MAGIC-0000000001",
    "submission_status": STATUS.DISSEMINATED,
    "transition_name": [
        "ready_for_certification",
        "auditor_certified",
        "auditee_certified",
        "certified",
        "submitted",
        "disseminated",
    ],
    "transition_date": [
        "2023-09-26T00:00:00.000Z",
        "2023-09-26T10:11:52.000Z",
        "2023-09-26T13:19:56.000Z",
        "2023-09-26T00:00:00.000Z",
        "2023-09-26T00:00:00.000Z",
        "2024-01-20T01:12:35.065Z",
    ],
    "general_information": {
        "ein": "237399677",
        "auditee_uei": "GNU9RNVE6J68",
        "auditee_zip": "15942",
        "auditor_ein": "251390233",
        "auditee_city": "MINERAL POINT",
        "auditee_name": "JACKSON TOWNSHIP VOLUNTEER FIRE COMPANY",
        "auditee_email": "MS74CCHS@ATLANTICBB.NET",
        "auditee_state": "PA",
        "auditee_fiscal_period_end": "2022-12-31",
    },
}


def _make_chain():
    """
    Create:

        A1 -> B2 -> C3
    """
    sac_a_data = {
        **deepcopy(SAC),
        "report_id": "2022-42-MAGIC-0000000001",
        "submission_status": STATUS.RESUBMITTED,
    }

    sac_b_data = {
        **deepcopy(SAC),
        "report_id": "2022-42-MAGIC-0000000002",
        "submission_status": STATUS.RESUBMITTED,
    }

    sac_c_data = {
        **deepcopy(SAC),
        "report_id": "2022-42-MAGIC-0000000003",
        "submission_status": STATUS.DISSEMINATED,
    }

    sac_a = baker.make(
        SingleAuditChecklist,
        **sac_a_data,
    )

    sac_b = baker.make(
        SingleAuditChecklist,
        **sac_b_data,
    )

    sac_c = baker.make(
        SingleAuditChecklist,
        **sac_c_data,
    )

    sac_a.resubmission_meta = {
        "version": 1,
        "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
        "next_report_id": sac_b.report_id,
        "next_row_id": sac_b.id,
    }

    sac_b.resubmission_meta = {
        "version": 2,
        "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
        "previous_report_id": sac_a.report_id,
        "previous_row_id": sac_a.id,
        "next_report_id": sac_c.report_id,
        "next_row_id": sac_c.id,
    }

    sac_c.resubmission_meta = {
        "version": 3,
        "resubmission_status": RESUBMISSION_STATUS.MOST_RECENT,
        "previous_report_id": sac_b.report_id,
        "previous_row_id": sac_b.id,
    }

    SingleAuditChecklist.objects.bulk_update(
        [sac_a, sac_b, sac_c],
        ["resubmission_meta"],
    )

    return sac_a, sac_b, sac_c


class SuppressAuditTests(TestCase):
    def setUp(self):
        self.user = baker.make(
            User,
            email="admin@example.com",
            is_staff=True,
        )

    def _make_sac(self, status=STATUS.DISSEMINATED):
        sac_data = {
            **deepcopy(SAC),
            "submission_status": status,
        }

        return baker.make(
            SingleAuditChecklist,
            **sac_data,
        )

    def test_suppress_standalone_audit(self):
        sac = self._make_sac()

        suppress_audit(
            sac.report_id,
            self.user.email,
        )

        sac.refresh_from_db()

        self.assertEqual(
            sac.submission_status,
            STATUS.FLAGGED_FOR_REMOVAL,
        )
        self.assertEqual(
            sac.transition_name[-1],
            STATUS.FLAGGED_FOR_REMOVAL,
        )

    def test_reject_non_staff_user(self):
        user = baker.make(
            User,
            email="not-staff@example.com",
            is_staff=False,
        )

        sac = self._make_sac()

        with self.assertRaisesRegex(
            ValueError,
            "No FAC staff user found",
        ):
            suppress_audit(
                sac.report_id,
                user.email,
            )

    def test_reject_missing_report_id(self):
        with self.assertRaisesRegex(
            ValueError,
            "No SAC found",
        ):
            suppress_audit(
                "missing-report-id",
                self.user.email,
            )

    def test_reject_invalid_status(self):
        sac = self._make_sac(
            STATUS.IN_PROGRESS,
        )

        with self.assertRaisesRegex(
            ValueError,
            "cannot be suppressed",
        ):
            suppress_audit(
                sac.report_id,
                self.user.email,
            )

    def test_suppress_audit_removes_dissemination_rows(self):
        sac = self._make_sac()

        general = baker.make(
            General,
            report_id=sac.report_id,
            is_public=True,
        )

        additional_ein = baker.make(
            AdditionalEin,
            report_id=general,
        )

        federal_award = baker.make(
            FederalAward,
            report_id=general,
        )

        # Confirm the dissemination records exist before suppression.
        self.assertTrue(General.objects.filter(report_id=sac.report_id).exists())
        self.assertTrue(AdditionalEin.objects.filter(pk=additional_ein.pk).exists())
        self.assertTrue(FederalAward.objects.filter(pk=federal_award.pk).exists())

        suppress_audit(
            sac.report_id,
            self.user.email,
        )

        # All dissemination records for the suppressed report are removed.
        self.assertFalse(General.objects.filter(report_id=sac.report_id).exists())
        self.assertFalse(AdditionalEin.objects.filter(pk=additional_ein.pk).exists())
        self.assertFalse(FederalAward.objects.filter(pk=federal_award.pk).exists())

        # The SAC itself is retained for curation.
        sac.refresh_from_db()

        self.assertEqual(
            sac.submission_status,
            STATUS.FLAGGED_FOR_REMOVAL,
        )

    def test_suppression_rolls_back_if_redissemination_fails(self):
        first, middle, last = _make_chain()

        general = baker.make(
            General,
            report_id=middle.report_id,
            is_public=True,
        )

        original_first_meta = deepcopy(first.resubmission_meta)
        original_middle_meta = deepcopy(middle.resubmission_meta)
        original_last_meta = deepcopy(last.resubmission_meta)

        with patch.object(
            SingleAuditChecklist,
            "redisseminate",
            return_value={"errors": ["Redissemination failed"]},
        ):
            with self.assertRaises(RuntimeError):
                suppress_audit(
                    report_id=middle.report_id,
                    email=self.user.email,
                )

        first.refresh_from_db()
        middle.refresh_from_db()
        last.refresh_from_db()

        self.assertEqual(first.resubmission_meta, original_first_meta)
        self.assertEqual(middle.resubmission_meta, original_middle_meta)
        self.assertEqual(last.resubmission_meta, original_last_meta)

        self.assertEqual(first.submission_status, STATUS.RESUBMITTED)
        self.assertEqual(middle.submission_status, STATUS.RESUBMITTED)
        self.assertEqual(last.submission_status, STATUS.DISSEMINATED)

        self.assertTrue(General.objects.filter(pk=general.pk).exists())

    @patch.object(
        SingleAuditChecklist,
        "redisseminate",
        return_value=True,
    )
    def test_suppress_first_report_relinks_chain(self, mock_redisseminate):
        first, middle, last = _make_chain()

        suppress_audit(
            report_id=first.report_id,
            email=self.user.email,
        )

        first.refresh_from_db()
        middle.refresh_from_db()
        last.refresh_from_db()

        self.assertEqual(
            first.submission_status,
            STATUS.FLAGGED_FOR_REMOVAL,
        )

        self.assertNotIn(
            "previous_report_id",
            middle.resubmission_meta,
        )
        self.assertNotIn(
            "previous_row_id",
            middle.resubmission_meta,
        )

        self.assertEqual(
            middle.resubmission_meta["version"],
            1,
        )
        self.assertEqual(
            last.resubmission_meta["version"],
            2,
        )

        self.assertEqual(
            last.resubmission_meta["previous_report_id"],
            middle.report_id,
        )

    @patch.object(
        SingleAuditChecklist,
        "redisseminate",
        return_value=True,
    )
    def test_suppress_middle_report_relinks_chain(self, mock_redisseminate):
        first, middle, last = _make_chain()

        suppress_audit(
            report_id=middle.report_id,
            email=self.user.email,
        )

        first.refresh_from_db()
        middle.refresh_from_db()
        last.refresh_from_db()

        self.assertEqual(
            middle.submission_status,
            STATUS.FLAGGED_FOR_REMOVAL,
        )

        self.assertEqual(
            first.resubmission_meta["next_report_id"],
            last.report_id,
        )
        self.assertEqual(
            first.resubmission_meta["next_row_id"],
            last.id,
        )

        self.assertEqual(
            last.resubmission_meta["previous_report_id"],
            first.report_id,
        )
        self.assertEqual(
            last.resubmission_meta["previous_row_id"],
            first.id,
        )

        self.assertEqual(
            last.resubmission_meta["version"],
            2,
        )

    @patch.object(
        SingleAuditChecklist,
        "redisseminate",
        return_value=True,
    )
    def test_suppress_last_report_makes_previous_most_recent(
        self,
        mock_redisseminate,
    ):
        first, middle, last = _make_chain()

        suppress_audit(
            report_id=last.report_id,
            email=self.user.email,
        )

        first.refresh_from_db()
        middle.refresh_from_db()
        last.refresh_from_db()

        self.assertEqual(
            last.submission_status,
            STATUS.FLAGGED_FOR_REMOVAL,
        )

        self.assertNotIn(
            "next_report_id",
            middle.resubmission_meta,
        )
        self.assertNotIn(
            "next_row_id",
            middle.resubmission_meta,
        )

        self.assertEqual(
            middle.resubmission_meta["version"],
            2,
        )

        self.assertEqual(
            middle.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.MOST_RECENT,
        )

        self.assertEqual(
            middle.submission_status,
            STATUS.DISSEMINATED,
        )

    @patch.object(
        SingleAuditChecklist,
        "redisseminate",
        autospec=True,
        return_value=True,
    )
    def test_suppressed_report_is_not_redisseminated(
        self,
        mock_redisseminate,
    ):
        first, middle, last = _make_chain()

        suppress_audit(
            report_id=middle.report_id,
            email=self.user.email,
        )

        redisseminated_ids = {
            call.args[0].report_id for call in mock_redisseminate.call_args_list
        }

        self.assertEqual(
            redisseminated_ids,
            {
                first.report_id,
                last.report_id,
            },
        )


class RepairResubmissionChainTests(TestCase):
    def setUp(self):
        self.user = baker.make(User, is_staff=True)

    def test_remove_first_sac(self):
        """A1 -> B2 -> C3 becomes B1 -> C2."""
        sac_a, sac_b, sac_c = _make_chain()

        repair_resubmission_chain(sac_a, self.user)

        sac_b.refresh_from_db()
        sac_c.refresh_from_db()

        self.assertNotIn(
            "previous_report_id",
            sac_b.resubmission_meta,
        )
        self.assertNotIn(
            "previous_row_id",
            sac_b.resubmission_meta,
        )
        self.assertEqual(
            sac_b.resubmission_meta["version"],
            1,
        )

        self.assertEqual(
            sac_c.resubmission_meta["previous_report_id"],
            sac_b.report_id,
        )
        self.assertEqual(
            sac_c.resubmission_meta["version"],
            2,
        )
        self.assertEqual(
            sac_b.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.DEPRECATED,
        )
        self.assertEqual(
            sac_b.submission_status,
            STATUS.RESUBMITTED,
        )

        self.assertEqual(
            sac_c.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.MOST_RECENT,
        )
        self.assertEqual(
            sac_c.submission_status,
            STATUS.DISSEMINATED,
        )

    def test_remove_middle_sac(self):
        """A1 -> B2 -> C3 becomes A1 -> C2."""
        sac_a, sac_b, sac_c = _make_chain()

        repair_resubmission_chain(sac_b, self.user)

        sac_a.refresh_from_db()
        sac_c.refresh_from_db()

        self.assertEqual(
            sac_a.resubmission_meta["next_report_id"],
            sac_c.report_id,
        )
        self.assertEqual(
            sac_a.resubmission_meta["next_row_id"],
            sac_c.id,
        )

        self.assertEqual(
            sac_c.resubmission_meta["previous_report_id"],
            sac_a.report_id,
        )
        self.assertEqual(
            sac_c.resubmission_meta["previous_row_id"],
            sac_a.id,
        )
        self.assertEqual(
            sac_c.resubmission_meta["version"],
            2,
        )
        self.assertEqual(
            sac_a.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.DEPRECATED,
        )
        self.assertEqual(
            sac_a.submission_status,
            STATUS.RESUBMITTED,
        )

        self.assertEqual(
            sac_c.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.MOST_RECENT,
        )
        self.assertEqual(
            sac_c.submission_status,
            STATUS.DISSEMINATED,
        )

    def test_remove_last_sac(self):
        """A1 -> B2 -> C3 becomes A1 -> B2."""
        sac_a, sac_b, sac_c = _make_chain()

        repair_resubmission_chain(sac_c, self.user)

        sac_b.refresh_from_db()

        self.assertNotIn(
            "next_report_id",
            sac_b.resubmission_meta,
        )
        self.assertNotIn(
            "next_row_id",
            sac_b.resubmission_meta,
        )
        self.assertEqual(
            sac_b.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.MOST_RECENT,
        )
        self.assertEqual(
            sac_b.submission_status,
            STATUS.DISSEMINATED,
        )

    def test_remove_middle_sac_renumbers_all_following_sacs(self):
        """A1 -> B2 -> C3 -> D4 becomes A1 -> C2 -> D3."""
        sac_a, sac_b, sac_c = _make_chain()

        sac_d_data = {
            **deepcopy(SAC),
            "report_id": "2022-42-MAGIC-0000000004",
            "submission_status": STATUS.DISSEMINATED,
        }

        sac_d = baker.make(
            SingleAuditChecklist,
            **sac_d_data,
        )

        # C is no longer the most recent record.
        sac_c.submission_status = STATUS.RESUBMITTED
        sac_c.resubmission_meta = {
            **sac_c.resubmission_meta,
            "resubmission_status": RESUBMISSION_STATUS.DEPRECATED,
            "next_report_id": sac_d.report_id,
            "next_row_id": sac_d.id,
        }

        sac_d.resubmission_meta = {
            "version": 4,
            "resubmission_status": RESUBMISSION_STATUS.MOST_RECENT,
            "previous_report_id": sac_c.report_id,
            "previous_row_id": sac_c.id,
        }

        SingleAuditChecklist.objects.bulk_update(
            [sac_c, sac_d],
            [
                "submission_status",
                "resubmission_meta",
            ],
        )

        repair_resubmission_chain(
            sac_b,
            self.user,
        )

        sac_a.refresh_from_db()
        sac_c.refresh_from_db()
        sac_d.refresh_from_db()

        # A now points directly to C.
        self.assertEqual(
            sac_a.resubmission_meta["next_report_id"],
            sac_c.report_id,
        )
        self.assertEqual(
            sac_a.resubmission_meta["next_row_id"],
            sac_c.id,
        )

        # C becomes version 2 and points back to A.
        self.assertEqual(
            sac_c.resubmission_meta["version"],
            2,
        )
        self.assertEqual(
            sac_c.resubmission_meta["previous_report_id"],
            sac_a.report_id,
        )
        self.assertEqual(
            sac_c.resubmission_meta["previous_row_id"],
            sac_a.id,
        )

        # D must also be renumbered from version 4 to version 3.
        self.assertEqual(
            sac_d.resubmission_meta["version"],
            3,
        )
        self.assertEqual(
            sac_d.resubmission_meta["previous_report_id"],
            sac_c.report_id,
        )
        self.assertEqual(
            sac_d.resubmission_meta["previous_row_id"],
            sac_c.id,
        )

        # D remains the most recent disseminated audit.
        self.assertEqual(
            sac_d.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.MOST_RECENT,
        )
        self.assertEqual(
            sac_d.submission_status,
            STATUS.DISSEMINATED,
        )

    def test_broken_previous_link_raises_error(self):
        sac_a, sac_b, sac_c = _make_chain()

        sac_b.resubmission_meta = {
            **sac_b.resubmission_meta,
            "previous_row_id": 999999,
        }
        sac_b.save()

        with self.assertRaisesRegex(
            ValueError,
            "Broken resubmission chain",
        ):
            repair_resubmission_chain(
                sac_b,
                self.user,
            )

    def test_broken_next_link_raises_error(self):
        sac_a, sac_b, sac_c = _make_chain()

        sac_b.resubmission_meta = {
            **sac_b.resubmission_meta,
            "next_row_id": 999999,
        }
        sac_b.save()

        with self.assertRaisesRegex(
            ValueError,
            "Broken resubmission chain",
        ):
            repair_resubmission_chain(
                sac_b,
                self.user,
            )


class AdministrativeRemovalTests(TestCase):
    def setUp(self):
        self.user = baker.make(User, is_staff=True)

    def test_flag_disseminated_sac_for_removal(self):
        sac_data = {
            **deepcopy(SAC),
            "submission_status": STATUS.DISSEMINATED,
        }
        sac = baker.make(
            SingleAuditChecklist,
            **sac_data,
        )

        original_transition_count = len(sac.transition_name)

        _flag_sac_for_administrative_removal(
            sac,
            self.user,
        )

        sac.refresh_from_db()

        self.assertEqual(
            sac.submission_status,
            STATUS.FLAGGED_FOR_REMOVAL,
        )
        self.assertEqual(
            sac.transition_name[-1],
            STATUS.FLAGGED_FOR_REMOVAL,
        )
        self.assertEqual(
            len(sac.transition_name),
            original_transition_count + 1,
        )
        self.assertEqual(
            len(sac.transition_name),
            len(sac.transition_date),
        )
