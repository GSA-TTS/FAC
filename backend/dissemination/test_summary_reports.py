from django.test import TestCase

from dissemination.summary_reports import generate_summary_report
from dissemination.models import General

from model_bakery import baker


class ExportTests(TestCase):
    def test_generate_summary_report_returns_filename(self):
        general = baker.make(General, _quantity=100)

        report_ids = [g.report_id for g in general]
        filename = generate_summary_report(report_ids)

        self.assertTrue(filename.startswith, "bulk-")
        self.assertTrue(filename.endswith, ".xlsx")
