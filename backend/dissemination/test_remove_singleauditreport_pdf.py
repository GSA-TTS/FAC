from django.test import TestCase
from unittest.mock import patch
from audit.models.models import SingleAuditChecklist, SingleAuditReportFile
from dissemination.remove_singleauditreport_pdf import remove_singleauditreport_pdf
from model_bakery import baker


class TestRemoveSingleAuditReportPDF(TestCase):

    @patch("dissemination.remove_singleauditreport_pdf.delete_files_in_bulk")
    def test_remove_singleauditreport_pdf_success(self, mock_delete_files_in_bulk):
        sac = baker.make(SingleAuditChecklist, report_id="1900-01-GSAFAC-0000000001")
        baker.make(
            SingleAuditReportFile,
            filename="singleauditreport/1900-01-GSAFAC-0000000001.pdf",
            sac=sac,
        )

        remove_singleauditreport_pdf(sac)

        # Assert that delete_files_in_bulk is called with correct arguments
        mock_delete_files_in_bulk.assert_called_once_with(
            ["singleauditreport/1900-01-GSAFAC-0000000001.pdf"], sac.report_id
        )

    @patch("dissemination.remove_singleauditreport_pdf.delete_files_in_bulk")
    def test_remove_singleauditreport_pdf_no_files(self, mock_delete_files_in_bulk):
        sac = baker.make(SingleAuditChecklist, report_id="1900-01-GSAFAC-0000000002")

        remove_singleauditreport_pdf(sac)

        mock_delete_files_in_bulk.assert_not_called()
