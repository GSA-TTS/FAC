from django.test import TestCase
from unittest.mock import patch
from audit.models.models import ExcelFile, SingleAuditChecklist
from model_bakery import baker

from dissemination.remove_workbook_artifacts import removed_workbook_artifacts


class RemovedWorkbookArtifactsTestCase(TestCase):

    @patch("dissemination.remove_workbook_artifacts.delete_files_in_bulk")
    def test_removed_workbook_artifacts_success(self, mock_delete_files_in_bulk):
        sac = baker.make(
            SingleAuditChecklist,
            submission_status=SingleAuditChecklist.STATUS.IN_PROGRESS,
            report_id="test_report_id",
        )

        # Create ExcelFile instances
        excel_file_1 = baker.make(ExcelFile, sac=sac, form_section="fake_section")
        excel_file_2 = baker.make(
            ExcelFile, sac=sac, form_section="another_fake_section"
        )

        removed_workbook_artifacts(sac)

        # Assert that the ExcelFile instances are deleted
        self.assertFalse(ExcelFile.objects.filter(sac=sac).exists())

        # Assert S3 bulk delete was called with the correct filenames
        mock_delete_files_in_bulk.assert_called_once_with(
            [
                f"excel/{sac.report_id}--{excel_file_1.form_section}.xlsx",
                f"excel/{sac.report_id}--{excel_file_2.form_section}.xlsx",
            ],
            sac,
        )

    @patch("dissemination.remove_workbook_artifacts.delete_files_in_bulk")
    def test_removed_workbook_artifacts_no_files(self, mock_delete_files_in_bulk):
        sac = baker.make(
            SingleAuditChecklist,
            submission_status=SingleAuditChecklist.STATUS.IN_PROGRESS,
            report_id="test_report_id",
        )

        # Ensure no ExcelFile instances exist for this SAC
        ExcelFile.objects.filter(sac=sac).delete()

        removed_workbook_artifacts(sac)

        # Assert that no ExcelFile instances exist
        self.assertFalse(ExcelFile.objects.filter(sac=sac).exists())

        # Assert S3 bulk delete was not called
        mock_delete_files_in_bulk.assert_not_called()