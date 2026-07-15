from django.test import TestCase
from model_bakery import baker

from audit.models import SingleAuditChecklist
from audit.models.constants import RESUBMISSION_ACTION
import audit.views.cross_validation


class ValidateResubmissionMetadataTests(TestCase):
    def test_non_resubmission_returns_no_errors(self):
        sac = baker.make(
            SingleAuditChecklist,
            resubmission_meta=None,
        )

        errors = audit.views.cross_validation._validate_resubmission_metadata(sac)

        self.assertEqual(errors, [])

    def test_valid_audit_pdf_resubmission_returns_no_errors(self):
        sac = baker.make(
            SingleAuditChecklist,
            resubmission_meta={
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.AUDIT_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": ["findings"],
                "non_material_change_reasons": [],
            },
        )

        errors = audit.views.cross_validation._validate_resubmission_metadata(sac)

        self.assertEqual(errors, [])

    def test_valid_sfsac_only_modification_returns_no_errors(self):
        sac = baker.make(
            SingleAuditChecklist,
            resubmission_meta={
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.SFSAC_ONLY,
                "resubmission_requester": ["auditor"],
                "material_change_reasons": [],
                "non_material_change_reasons": ["spelling"],
            },
        )

        errors = audit.views.cross_validation._validate_resubmission_metadata(sac)

        self.assertEqual(errors, [])

    def test_missing_requester_returns_error(self):
        sac = baker.make(
            SingleAuditChecklist,
            resubmission_meta={
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.AUDIT_PDF,
                "resubmission_requester": [],
                "material_change_reasons": ["findings"],
                "non_material_change_reasons": [],
            },
        )

        errors = audit.views.cross_validation._validate_resubmission_metadata(sac)

        self.assertIn(
            {"error": "At least one resubmission requester is required."},
            errors,
        )

    def test_missing_material_reasons_returns_error(self):
        sac = baker.make(
            SingleAuditChecklist,
            resubmission_meta={
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.AUDIT_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
            },
        )

        errors = audit.views.cross_validation._validate_resubmission_metadata(sac)

        self.assertIn(
            {
                "error": (
                    "At least one material change is required for an "
                    "audit PDF resubmission."
                )
            },
            errors,
        )

    def test_missing_non_material_reasons_returns_error(self):
        sac = baker.make(
            SingleAuditChecklist,
            resubmission_meta={
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.SFSAC_ONLY,
                "resubmission_requester": ["auditor"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
            },
        )

        errors = audit.views.cross_validation._validate_resubmission_metadata(sac)

        self.assertIn(
            {
                "error": (
                    "At least one non-material change is required for an "
                    "SF-SAC-only modification."
                )
            },
            errors,
        )
