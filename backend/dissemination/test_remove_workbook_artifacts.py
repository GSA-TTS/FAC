from django.test import TestCase
from unittest.mock import patch
from audit.models.models import ExcelFile, SingleAuditChecklist
from model_bakery import baker

from dissemination.remove_workbook_artifacts import (
    #    clean_artifacts,
    #    delete_workbooks,
    remove_workbook_artifacts,
)


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

        remove_workbook_artifacts(sac)

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

        remove_workbook_artifacts(sac)

        # Assert that no ExcelFile instances exist
        self.assertFalse(ExcelFile.objects.filter(sac=sac).exists())

        # Assert S3 bulk delete was not called
        mock_delete_files_in_bulk.assert_not_called()


# class CleanArtifactsTestCase(TestCase):

#     @patch("dissemination.remove_workbook_artifacts.batch_removal")
#     def test_clean_artifacts_success(self, mock_batch_removal):
#         # Create SAC instances
#         sac_1 = baker.make(SingleAuditChecklist, report_id="report_id_1")
#         sac_2 = baker.make(SingleAuditChecklist, report_id="report_id_2")

#         # Create ExcelFile instances
#         excel_file_1 = baker.make(ExcelFile, sac=sac_1, form_section="section_1")
#         excel_file_2 = baker.make(ExcelFile, sac=sac_2, form_section="section_2")

#         sac_list = [sac_1, sac_2]
#         clean_artifacts(sac_list)

#         # Assert that the ExcelFile instances are deleted
#         self.assertFalse(ExcelFile.objects.filter(sac__in=sac_list).exists())

#         # Assert S3 bulk delete was called with the correct filenames
#         mock_batch_removal.assert_called_once_with(
#             [
#                 f"excel/{sac_1.report_id}--{excel_file_1.form_section}.xlsx",
#                 f"excel/{sac_2.report_id}--{excel_file_2.form_section}.xlsx",
#             ],
#             sac_list,
#             {
#                 f"{sac_1.report_id}--{excel_file_1.form_section}.xlsx": sac_1,
#                 f"{sac_2.report_id}--{excel_file_2.form_section}.xlsx": sac_2,
#             },
#         )

#     @patch("dissemination.remove_workbook_artifacts.batch_removal")
#     def test_clean_artifacts_no_files(self, mock_batch_removal):
#         sac = baker.make(SingleAuditChecklist, report_id="test_report_id")

#         # Ensure no ExcelFile instances exist for this SAC
#         ExcelFile.objects.filter(sac=sac).delete()

#         clean_artifacts([sac])

#         # Assert that no ExcelFile instances exist
#         self.assertFalse(ExcelFile.objects.filter(sac=sac).exists())

#         # Assert S3 bulk delete was not called
#         mock_batch_removal.assert_not_called()


# class DeleteWorkbooksTestCase(TestCase):

#     @patch("dissemination.remove_workbook_artifacts.clean_artifacts")
#     def test_delete_workbooks_single_page(self, mock_clean_artifacts):
#         sac = baker.make(
#             SingleAuditChecklist,
#             AUDITYEAR=22,
#             submission_status=SingleAuditChecklist.STATUS.DISSEMINATED,
#         )
#         baker.make(ExcelFile, sac=sac, filename="file_1.xlsx")

#         delete_workbooks(22, page_size=10, pages=1)

#         # Assert clean_artifacts was called with the correct sac list
#         mock_clean_artifacts.assert_called_once()

#     @patch("dissemination.remove_workbook_artifacts.clean_artifacts")
#     def test_delete_workbooks_multiple_pages(self, mock_clean_artifacts):
#         sac_1 = baker.make(
#             SingleAuditChecklist,
#             AUDITYEAR=22,
#             submission_status=SingleAuditChecklist.STATUS.DISSEMINATED,
#         )
#         sac_2 = baker.make(
#             SingleAuditChecklist,
#             AUDITYEAR=22,
#             submission_status=SingleAuditChecklist.STATUS.DISSEMINATED,
#         )
#         baker.make(ExcelFile, sac=sac_1, filename="file_1.xlsx")
#         baker.make(ExcelFile, sac=sac_2, filename="file_2.xlsx")

#         delete_workbooks(22, page_size=1, pages=2)

#         # Assert clean_artifacts was called twice, once for each page
#         self.assertEqual(mock_clean_artifacts.call_count, 2)

#     @patch("dissemination.remove_workbook_artifacts.clean_artifacts")
#     def test_delete_workbooks_all_pages(self, mock_clean_artifacts):
#         sac_1 = baker.make(
#             SingleAuditChecklist,
#             AUDITYEAR=22,
#             submission_status=SingleAuditChecklist.STATUS.DISSEMINATED,
#         )
#         sac_2 = baker.make(
#             SingleAuditChecklist,
#             AUDITYEAR=22,
#             submission_status=SingleAuditChecklist.STATUS.DISSEMINATED,
#         )
#         baker.make(ExcelFile, sac=sac_1, filename="file_1.xlsx")
#         baker.make(ExcelFile, sac=sac_2, filename="file_2.xlsx")

#         delete_workbooks(22, page_size=1)

#         # Assert clean_artifacts was called twice, once for each page since we don't limit pages
#         self.assertEqual(mock_clean_artifacts.call_count, 2)
