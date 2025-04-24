from django.test import TestCase
from unittest.mock import patch
from audit.models import ExcelFile, Audit
from audit.models.constants import STATUS
from model_bakery import baker

from dissemination.remove_workbook_artifacts import (
    clean_artifacts,
    delete_workbooks,
    audit_remove_workbook_artifacts,
)


class RemovedWorkbookArtifactsTestCase(TestCase):

    @patch("dissemination.remove_workbook_artifacts.delete_files_in_bulk")
    def test_removed_workbook_artifacts_success(self, mock_delete_files_in_bulk):
        audit = baker.make(
            Audit,
            version=0,
            submission_status=STATUS.IN_PROGRESS,
            report_id="test_report_id",
        )

        # Create ExcelFile instances
        excel_file_1 = baker.make(ExcelFile, audit=audit, form_section="fake_section")
        excel_file_2 = baker.make(
            ExcelFile, audit=audit, form_section="another_fake_section"
        )

        audit_remove_workbook_artifacts(audit)

        # Assert that the ExcelFile instances are not deleted
        self.assertTrue(ExcelFile.objects.filter(audit=audit).exists())

        # Assert S3 bulk delete was called with the correct filenames
        mock_delete_files_in_bulk.assert_called_once_with(
            [
                f"excel/{audit.report_id}--{excel_file_1.form_section}.xlsx",
                f"excel/{audit.report_id}--{excel_file_2.form_section}.xlsx",
            ],
            audit.report_id,
        )

    @patch("dissemination.remove_workbook_artifacts.delete_files_in_bulk")
    def test_removed_workbook_artifacts_no_files(self, mock_delete_files_in_bulk):
        audit = baker.make(
            Audit,
            version=0,
            submission_status=STATUS.IN_PROGRESS,
            report_id="test_report_id",
        )

        # Ensure no ExcelFile instances exist for this SAC
        ExcelFile.objects.filter(audit=audit).delete()

        audit_remove_workbook_artifacts(audit)

        # Assert that no ExcelFile instances exist
        self.assertFalse(ExcelFile.objects.filter(audit=audit).exists())

        # Assert S3 bulk delete was not called
        mock_delete_files_in_bulk.assert_not_called()


class CleanArtifactsTestCase(TestCase):

    @patch("dissemination.remove_workbook_artifacts.batch_removal")
    def test_clean_artifacts_success(self, mock_batch_removal):
        # Create SAC instances
        audit_1 = baker.make(Audit, version=0, report_id="report_id_1")
        audit_2 = baker.make(Audit, version=0, report_id="report_id_2")

        # Create ExcelFile instances
        excel_file_1 = baker.make(ExcelFile, audit=audit_1, form_section="section_1")
        excel_file_2 = baker.make(ExcelFile, audit=audit_2, form_section="section_2")

        audit_list = [audit_1, audit_2]
        clean_artifacts(audit_list)

        # Assert that the ExcelFile instances still exist (no deletion)
        self.assertTrue(ExcelFile.objects.filter(audit__in=audit_list).exists())

        # Assert S3 bulk delete was called with the correct filenames
        mock_batch_removal.assert_called_once_with(
            [
                f"excel/{audit_1.report_id}--{excel_file_1.form_section}.xlsx",
                f"excel/{audit_2.report_id}--{excel_file_2.form_section}.xlsx",
            ],
            audit_list,
            {
                f"excel/{audit_1.report_id}--{excel_file_1.form_section}.xlsx": audit_1.report_id,
                f"excel/{audit_2.report_id}--{excel_file_2.form_section}.xlsx": audit_2.report_id,
            },
        )

    @patch("dissemination.remove_workbook_artifacts.batch_removal")
    def test_clean_artifacts_no_files(self, mock_batch_removal):
        audit = baker.make(Audit, version=0, report_id="test_report_id")

        # Ensure no ExcelFile instances exist for this SAC
        ExcelFile.objects.filter(audit=audit).delete()

        clean_artifacts([audit])

        # Assert that no ExcelFile instances exist
        self.assertFalse(ExcelFile.objects.filter(audit=audit).exists())

        # Assert S3 bulk delete was not called
        mock_batch_removal.assert_not_called()


class DeleteWorkbooksTestCase(TestCase):

    def setUp(self):
        # Common setup for SAC instances
        self.audit_1 = baker.make(Audit, version=0, report_id="report_1")
        self.audit_2 = baker.make(Audit, version=0, report_id="report_2")
        # Create associated ExcelFile instances
        self.excel_file_1 = baker.make(
            ExcelFile, audit=self.audit_1, form_section="section_1"
        )
        self.excel_file_2 = baker.make(
            ExcelFile, audit=self.audit_2, form_section="section_2"
        )
        # Update submission status to DISSEMINATED
        self.audit_1.submission_status = STATUS.DISSEMINATED
        self.audit_2.submission_status = STATUS.DISSEMINATED
        self.audit_1.save()
        self.audit_2.save()

    @patch("dissemination.remove_workbook_artifacts.clean_artifacts")
    def test_delete_workbooks_single_page(self, mock_clean_artifacts):
        """Test delete_workbooks with a single page of workbooks"""
        delete_workbooks(partition_number=1, total_partitions=1, page_size=10, pages=1)

        mock_clean_artifacts.assert_called_once_with([self.audit_1, self.audit_2])

    @patch("dissemination.remove_workbook_artifacts.clean_artifacts")
    def test_delete_workbooks_multiple_pages(self, mock_clean_artifacts):
        """Test delete_workbooks with multiple pages of workbooks"""
        delete_workbooks(partition_number=1, total_partitions=1, page_size=1, pages=2)

        self.assertEqual(mock_clean_artifacts.call_count, 2)

        mock_clean_artifacts.assert_any_call([self.audit_1])
        mock_clean_artifacts.assert_any_call([self.audit_2])

    @patch("dissemination.remove_workbook_artifacts.clean_artifacts")
    def test_delete_workbooks_all_pages(self, mock_clean_artifacts):
        """Test delete_workbooks with all pages of workbooks"""

        delete_workbooks(partition_number=1, total_partitions=1, page_size=1)

        self.assertEqual(mock_clean_artifacts.call_count, 2)

        mock_clean_artifacts.assert_any_call([self.audit_1])
        mock_clean_artifacts.assert_any_call([self.audit_2])
