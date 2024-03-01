from django.test import TestCase

from dissemination.summary_reports import (
    can_read_tribal_disclaimer,
    cannot_read_tribal_disclaimer,
    generate_summary_report,
    _get_tribal_report_ids,
    insert_dissem_coversheet,
)
from dissemination.models import General

from model_bakery import baker
import openpyxl as pyxl


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

    def test_insert_dissem_coversheet_tribal_can_read(self):
        workbook = pyxl.Workbook()
        insert_dissem_coversheet(workbook, True, True)
        coversheet = workbook.get_sheet_by_name("Coversheet")

        self.assertEqual(coversheet["B3"].value, can_read_tribal_disclaimer)

    def test_insert_dissem_coversheet_tribal_cannot_read(self):
        workbook = pyxl.Workbook()
        insert_dissem_coversheet(workbook, True, False)
        coversheet = workbook.get_sheet_by_name("Coversheet")

        self.assertEqual(coversheet["B3"].value, cannot_read_tribal_disclaimer)

    def test_insert_dissem_coversheet_public(self):
        workbook = pyxl.Workbook()
        insert_dissem_coversheet(workbook, False, False)
        coversheet = workbook.get_sheet_by_name("Coversheet")

        self.assertEqual(coversheet["B3"].value, None)
