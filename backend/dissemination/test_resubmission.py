from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from audit.models.constants import RESUBMISSION_STATUS
from dissemination.models import General, Resubmission


def create_general(report_id, **overrides):
    now = timezone.now()

    defaults = {
        "report_id": report_id,
        "auditee_certify_name": "Auditee Certifier",
        "auditee_certify_title": "CFO",
        "auditor_certify_name": "Auditor Certifier",
        "auditor_certify_title": "Audit Partner",
        "auditee_contact_name": "Auditee Contact",
        "auditee_email": "auditee@example.com",
        "auditee_name": "Test Auditee",
        "auditee_phone": "555-111-2222",
        "auditee_contact_title": "Finance Director",
        "auditee_address_line_1": "123 Main St",
        "auditee_city": "Baltimore",
        "auditee_state": "MD",
        "auditee_ein": "123456789",
        "auditee_uei": f"UEI-{report_id}",
        "is_additional_ueis": False,
        "auditee_zip": "21201",
        "auditor_phone": "555-333-4444",
        "auditor_state": "MD",
        "auditor_city": "Baltimore",
        "auditor_contact_title": "Audit Manager",
        "auditor_address_line_1": "456 Market St",
        "auditor_zip": "21202",
        "auditor_country": "USA",
        "auditor_contact_name": "Auditor Contact",
        "auditor_email": "auditor@example.com",
        "auditor_firm_name": "Test Audit Firm",
        "auditor_foreign_address": False,
        "auditor_ein": "987654321",
        "date_created": now,
        "ready_for_certification_date": now,
        "auditor_certified_date": now,
        "auditee_certified_date": now,
        "submitted_date": now,
        "fac_accepted_date": now,
        "fy_end_date": "2024-12-31",
        "fy_start_date": "2024-01-01",
        "audit_year": "2024",
        "audit_type": "single-audit",
        "gaap_results": "unmodified",
        "sp_framework_basis": "gaap",
        "is_sp_framework_required": False,
        "sp_framework_opinions": "unmodified",
        "is_going_concern_included": False,
        "is_internal_control_deficiency_disclosed": False,
        "is_internal_control_material_weakness_disclosed": False,
        "is_material_noncompliance_disclosed": False,
        "is_aicpa_audit_guide_included": False,
        "dollar_threshold": Decimal("750000.00"),
        "is_low_risk_auditee": False,
        "agencies_with_prior_findings": "none",
        "entity_type": "local-government",
        "number_months": 12,
        "audit_period_covered": "annual",
        "total_amount_expended": Decimal("1000000.00"),
        "type_audit_code": "S",
        "is_public": True,
        "data_source": "test",
        "resubmission_version": 1,
    }

    defaults.update(overrides)
    return General.objects.create(**defaults)


class ResubmissionModelTests(TestCase):
    def test_second_resubmission_of_same_parent_is_blocked(self):
        """
        Simulates Alice vs Bob race condition.

        Alice creates R2 from R1.
        Bob attempts to create R3 from R1.

        DB should block the second one due to unique(previous_report_id),
        preventing branching chains.
        """
        r1 = create_general("R1")
        r2 = create_general("R2")
        r3 = create_general("R3")

        Resubmission.objects.create(
            report_id=r2,
            version=2,
            status=RESUBMISSION_STATUS.MOST_RECENT,
            previous_report_id=r1.report_id,
        )

        with self.assertRaises(IntegrityError):
            Resubmission.objects.create(
                report_id=r3,
                version=2,
                status=RESUBMISSION_STATUS.MOST_RECENT,
                previous_report_id=r1.report_id,
            )

    def test_only_one_resubmission_row_per_report(self):
        """
        Ensures OneToOneField on report_id is enforced.
        """
        r1 = create_general("R10")
        r2 = create_general("R11")

        Resubmission.objects.create(
            report_id=r2,
            version=2,
            status=RESUBMISSION_STATUS.MOST_RECENT,
            previous_report_id=r1.report_id,
        )

        with self.assertRaises(IntegrityError):
            Resubmission.objects.create(
                report_id=r2,
                version=3,
                status=RESUBMISSION_STATUS.DEPRECATED,
                previous_report_id="R9",
            )

    def test_previous_and_next_cannot_be_equal(self):
        """
        Ensures previous_report_id != next_report_id.
        """
        r2 = create_general("R20")

        with self.assertRaises(IntegrityError):
            Resubmission.objects.create(
                report_id=r2,
                version=2,
                status=RESUBMISSION_STATUS.MOST_RECENT,
                previous_report_id="R19",
                next_report_id="R19",
            )

    def test_multiple_null_previous_report_ids_allowed(self):
        """
        Multiple root records (no previous) should be allowed.
        """
        r1 = create_general("R30")
        r2 = create_general("R31")

        Resubmission.objects.create(
            report_id=r1,
            version=1,
            status=RESUBMISSION_STATUS.MOST_RECENT,
            previous_report_id=None,
        )

        Resubmission.objects.create(
            report_id=r2,
            version=1,
            status=RESUBMISSION_STATUS.MOST_RECENT,
            previous_report_id=None,
        )

        self.assertEqual(
            Resubmission.objects.filter(previous_report_id__isnull=True).count(),
            2,
        )

    def test_multiple_null_next_report_ids_allowed(self):
        """
        Multiple most-recent records with null next_report_id should be allowed.
        """
        r1 = create_general("R40")
        r2 = create_general("R41")

        Resubmission.objects.create(
            report_id=r1,
            version=1,
            status=RESUBMISSION_STATUS.MOST_RECENT,
            next_report_id=None,
        )

        Resubmission.objects.create(
            report_id=r2,
            version=1,
            status=RESUBMISSION_STATUS.MOST_RECENT,
            next_report_id=None,
        )

        self.assertEqual(
            Resubmission.objects.filter(next_report_id__isnull=True).count(),
            2,
        )
