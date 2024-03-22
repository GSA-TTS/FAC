from dissemination.test_search import TestMaterializedViewBuilder
from dissemination.summary_reports import (
    can_read_tribal_disclaimer,
    cannot_read_tribal_disclaimer,
    gather_report_data_dissemination,
    generate_summary_report,
    get_tribal_report_ids,
    insert_dissem_coversheet,
)
from dissemination.models import FederalAward, General, CapText, Note, FindingText

from model_bakery import baker
import openpyxl as pyxl


class SummaryReportTests(TestMaterializedViewBuilder):
    def test_generate_summary_report_returns_filename(self):
        """The filename returned should be correctly formatted"""
        general = baker.make(General, _quantity=100)
        report_ids = [g.report_id for g in general]

        for g in general:
            baker.make(FederalAward, report_id=g)
        self.refresh_materialized_view()

        filename = generate_summary_report(report_ids)

        self.assertTrue(filename.startswith, "fac-summary-report-")
        self.assertTrue(filename.endswith, ".xlsx")

    def test_get_tribal_report_ids(self):
        """The report_ids returned should only belong to tribal audits"""
        public_general = baker.make(General, _quantity=3, is_public=True)
        tribal_general = baker.make(General, _quantity=2, is_public=False)
        public_report_ids = [g.report_id for g in public_general]
        tribal_report_ids = [g.report_id for g in tribal_general]

        for g in public_general:
            baker.make(FederalAward, report_id=g)
        for g in tribal_general:
            baker.make(FederalAward, report_id=g)

        self.refresh_materialized_view()

        (ls, _) = get_tribal_report_ids(public_report_ids + tribal_report_ids)
        self.assertEqual(
            len(ls),
            2,
        )

    def test_get_tribal_report_ids_no_tribal(self):
        """No report_ids should be returned for entirely public audits"""
        public_general = baker.make(General, _quantity=3, is_public=True)
        public_report_ids = [g.report_id for g in public_general]

        for g in public_general:
            baker.make(FederalAward, report_id=g)

        self.refresh_materialized_view()

        (ls, _) = get_tribal_report_ids(public_report_ids)
        self.assertEqual(
            len(ls),
            0,
        )

    def test_get_tribal_report_ids_no_public(self):
        """report_ids returned should be the same as those given if they're all tribal"""
        tribal_general = baker.make(General, _quantity=2, is_public=False)
        tribal_report_ids = [g.report_id for g in tribal_general]

        for g in tribal_general:
            baker.make(FederalAward, report_id=g)

        self.refresh_materialized_view()

        (ls, _) = get_tribal_report_ids(tribal_report_ids)
        self.assertListEqual(
            ls,
            tribal_report_ids,
        )

    def test_insert_dissem_coversheet_tribal_can_read(self):
        """Coversheet should have correct disclaimer for tribal data that can be read"""
        workbook = pyxl.Workbook()
        insert_dissem_coversheet(workbook, True, True)
        coversheet = workbook.get_sheet_by_name("Coversheet")

        self.assertEqual(coversheet["B3"].value, can_read_tribal_disclaimer)

    def test_insert_dissem_coversheet_tribal_cannot_read(self):
        """Coversheet should have correct disclaimer for tribal data that cannot be read"""
        workbook = pyxl.Workbook()
        insert_dissem_coversheet(workbook, True, False)
        coversheet = workbook.get_sheet_by_name("Coversheet")

        self.assertEqual(coversheet["B3"].value, cannot_read_tribal_disclaimer)

    def test_insert_dissem_coversheet_public(self):
        """Coversheet should have no disclaimer for tribal data if all data is public"""
        workbook = pyxl.Workbook()
        insert_dissem_coversheet(workbook, False, False)
        coversheet = workbook.get_sheet_by_name("Coversheet")

        self.assertEqual(coversheet["B3"].value, None)

    def _test_gather_report_data_dissemination_helper(self, include_private):
        """
        Helper to create public and tribal audits, generate a summary, and check the
        correct tribal data is omitted
        """
        # Create public audit with relevant sections
        public_general = baker.make(General, is_public=True)
        public_report_ids = [public_general.report_id]
        baker.make(CapText, report_id=public_general)
        baker.make(Note, report_id=public_general)
        baker.make(FindingText, report_id=public_general)

        # Create tribal audit with relevant sections
        tribal_general = baker.make(General, is_public=False)
        tribal_report_ids = [tribal_general.report_id]
        baker.make(CapText, report_id=tribal_general)
        baker.make(Note, report_id=tribal_general)
        baker.make(FindingText, report_id=tribal_general)

        # Get the data that constitutes the summary workbook
        (data, _) = gather_report_data_dissemination(
            public_report_ids + tribal_report_ids,
            tribal_report_ids,
            include_private,
        )

        # These sheets should all omit rows containing the tribal report_id when !include_private
        private_sheets = ["captext", "note", "findingtext"]
        for sheet in private_sheets:
            found_public, found_tribal = False, False
            report_id_index = data[sheet]["field_names"].index("report_id")

            for row in data[sheet]["entries"]:
                if row[report_id_index] == public_general.report_id:
                    found_public = True
                elif row[report_id_index] == tribal_general.report_id:
                    found_tribal = True

            self.assertTrue(found_public)
            self.assertEqual(found_tribal, include_private)

    def test_gather_report_data_dissemination_exclude_private(self):
        """Summaries with tribal data and no access"""
        self._test_gather_report_data_dissemination_helper(False)

    def test_gather_report_data_dissemination_include_private(self):
        """Summaries with tribal data and access"""
        self._test_gather_report_data_dissemination_helper(True)
