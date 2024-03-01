from django.test import TestCase

from dissemination.summary_reports import (
    generate_summary_report,
    _get_tribal_report_ids,
)
from dissemination.models import General

from model_bakery import baker


class SummaryReportTests(TestCase):
    def test_generate_summary_report_returns_filename(self):
        general = baker.make(General, _quantity=100)

        report_ids = [g.report_id for g in general]
        filename = generate_summary_report(report_ids)

        self.assertTrue(filename.startswith, "fac-summary-report-")
        self.assertTrue(filename.endswith, ".xlsx")

    def test_get_tribal_report_ids(self):
        public_general = baker.make(General, _quantity=3, is_public=True)
        tribal_general = baker.make(General, _quantity=2, is_public=False)

        public_report_ids = [g.report_id for g in public_general]
        tribal_report_ids = [g.report_id for g in tribal_general]

        self.assertEqual(
            len(_get_tribal_report_ids(public_report_ids + tribal_report_ids)),
            2,
        )

    def test_get_tribal_report_ids_no_tribal(self):
        public_general = baker.make(General, _quantity=3, is_public=True)

        public_report_ids = [g.report_id for g in public_general]

        self.assertEqual(
            len(_get_tribal_report_ids(public_report_ids)),
            0,
        )

    def test_get_tribal_report_ids_no_public(self):
        tribal_general = baker.make(General, _quantity=2, is_public=False)

        tribal_report_ids = [g.report_id for g in tribal_general]

        self.assertEqual(
            len(_get_tribal_report_ids(tribal_report_ids)),
            2,
        )
