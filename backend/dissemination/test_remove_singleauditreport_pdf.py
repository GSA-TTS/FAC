from django.test import TestCase
from unittest.mock import patch
from model_bakery import baker

from audit.models import Audit, SingleAuditReportFile
from dissemination.remove_singleauditreport_pdf import (
    audit_remove_singleauditreport_pdf,
)


class TestRemoveSingleAuditReportPDF(TestCase):

    @patch("dissemination.remove_singleauditreport_pdf.delete_files_in_bulk")
    def test_remove_singleauditreport_pdf_success(self, mock_delete_files_in_bulk):
        audit = baker.make(Audit, version=0, report_id="1900-01-GSAFAC-0000000001")
        baker.make(
            SingleAuditReportFile,
            filename="singleauditreport/1900-01-GSAFAC-0000000001.pdf",
            audit=audit,
        )

        audit_remove_singleauditreport_pdf(audit)

        # Assert that delete_files_in_bulk is called with correct arguments
        mock_delete_files_in_bulk.assert_called_once_with(
            ["singleauditreport/1900-01-GSAFAC-0000000001.pdf"], audit.report_id
        )

    @patch("dissemination.remove_singleauditreport_pdf.delete_files_in_bulk")
    def test_remove_singleauditreport_pdf_no_files(self, mock_delete_files_in_bulk):
        audit = baker.make(Audit, version=0, report_id="1900-01-GSAFAC-0000000002")

        audit_remove_singleauditreport_pdf(audit)

        mock_delete_files_in_bulk.assert_not_called()
