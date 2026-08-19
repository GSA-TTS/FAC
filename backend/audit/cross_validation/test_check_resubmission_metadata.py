from django.test import SimpleTestCase

from audit.cross_validation.check_resubmission_metadata import (
    check_resubmission_metadata,
)

from audit.cross_validation.errors import (
    err_material_change_required,
    err_non_material_change_required,
    err_resubmission_requester_required,
)

from audit.models.constants import RESUBMISSION_ACTION


class CheckResubmissionMetadataTests(SimpleTestCase):
    def make_data(self, resubmission_meta=None):
        return {
            "sf_sac_sections": {},
            "sf_sac_meta": {
                "resubmission_meta": resubmission_meta,
            },
        }

    def test_non_resubmission_returns_no_errors(self):
        self.assertEqual(
            check_resubmission_metadata(self.make_data()),
            [],
        )

    def test_valid_audit_pdf_resubmission_returns_no_errors(self):
        data = self.make_data(
            {
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.AUDIT_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": ["findings"],
                "non_material_change_reasons": [],
            }
        )

        self.assertEqual(check_resubmission_metadata(data), [])

    def test_valid_non_material_pdf_resubmission_returns_no_errors(self):
        data = self.make_data(
            {
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.NON_MATERIAL_PDF,
                "resubmission_requester": ["auditor"],
                "material_change_reasons": [],
                "non_material_change_reasons": ["spelling"],
            }
        )

        self.assertEqual(check_resubmission_metadata(data), [])

    def test_valid_sfsac_only_resubmission_returns_no_errors(self):
        data = self.make_data(
            {
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.SFSAC_ONLY,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
                "sfsac_only_change_reasons": ["spelling"],
            }
        )

        self.assertEqual(check_resubmission_metadata(data), [])

    def test_missing_requester_returns_error(self):
        data = self.make_data(
            {
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.AUDIT_PDF,
                "resubmission_requester": [],
                "material_change_reasons": ["findings"],
                "non_material_change_reasons": [],
            }
        )

        self.assertIn(
            {"error": err_resubmission_requester_required()},
            check_resubmission_metadata(data),
        )

    def test_missing_material_reasons_returns_error(self):
        data = self.make_data(
            {
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.AUDIT_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
            }
        )

        self.assertIn(
            {"error": err_material_change_required()},
            check_resubmission_metadata(data),
        )

    def test_missing_non_material_reasons_returns_error(self):
        data = self.make_data(
            {
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.NON_MATERIAL_PDF,
                "resubmission_requester": ["auditor"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
            }
        )

        self.assertIn(
            {"error": err_non_material_change_required()},
            check_resubmission_metadata(data),
        )

    def test_missing_sfsac_only_reasons_returns_error(self):
        data = self.make_data(
            {
                "previous_report_id": "2024-01-GSAFAC-0000000001",
                "resubmission_action": RESUBMISSION_ACTION.SFSAC_ONLY,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
                "sfsac_only_change_reasons": [],
            }
        )

        self.assertIn(
            {"error": err_non_material_change_required()},
            check_resubmission_metadata(data),
        )
