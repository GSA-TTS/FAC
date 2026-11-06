from django.test import SimpleTestCase
from django.test import TestCase
from unittest.mock import patch
from types import SimpleNamespace

from dissemination.summary_reports import (
    can_read_tribal_disclaimer,
    cannot_read_tribal_disclaimer,
    gather_report_data_dissemination,
    generate_summary_report,
    get_tribal_report_ids,
    insert_dissem_coversheet,
    separate_notes_single_fields_from_array_fields,
)
from dissemination.models import (
    FederalAward,
    General,
    CapText,
    Note,
    FindingText,
    Finding,
)
from dissemination.test_utils import bake_unified

from model_bakery import baker
import openpyxl as pyxl


class SummaryReportTests(TestCase):
    def test_generate_summary_report_returns_filename(self):
        """The filename returned should be correctly formatted"""
        general = baker.make(General, _quantity=100)
        report_ids = [g.report_id for g in general]

        for g in general:
            fed = baker.make(FederalAward, report_id=g)
            bake_unified(g, [fed])

        filename, _ = generate_summary_report(report_ids)

        self.assertTrue(filename.startswith, "fac-summary-report-")
        self.assertTrue(filename.endswith, ".xlsx")

    def test_get_tribal_report_ids(self):
        """The report_ids returned should only belong to tribal audits"""
        public_general = baker.make(General, _quantity=3, is_public=True)
        tribal_general = baker.make(General, _quantity=2, is_public=False)
        public_report_ids = [g.report_id for g in public_general]
        tribal_report_ids = [g.report_id for g in tribal_general]

        for g in public_general:
            fed = baker.make(FederalAward, report_id=g)
            bake_unified(g, [fed])
        for g in tribal_general:
            baker.make(FederalAward, report_id=g)
            bake_unified(g, [fed])

        ls, _ = get_tribal_report_ids(public_report_ids + tribal_report_ids)
        self.assertEqual(
            len(ls),
            2,
        )

    def test_get_tribal_report_ids_no_tribal(self):
        """No report_ids should be returned for entirely public audits"""
        public_general = baker.make(General, _quantity=3, is_public=True)
        public_report_ids = [g.report_id for g in public_general]

        for g in public_general:
            fed = baker.make(FederalAward, report_id=g)
            bake_unified(g, [fed])

        ls, _ = get_tribal_report_ids(public_report_ids)
        self.assertEqual(
            len(ls),
            0,
        )

    def test_get_tribal_report_ids_no_public(self):
        """report_ids returned should be the same as those given if they're all tribal"""
        tribal_general = baker.make(General, _quantity=2, is_public=False)
        tribal_report_ids = [g.report_id for g in tribal_general]

        for g in tribal_general:
            fed = baker.make(FederalAward, report_id=g)
            bake_unified(g, [fed])

        ls, _ = get_tribal_report_ids(tribal_report_ids)
        # Somewhat misleadingly named - it asserts both count and content equivalence
        self.assertCountEqual(
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
        data, _ = gather_report_data_dissemination(
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


class SeparateNotesSingleFieldsFromArrayFields(SimpleTestCase):
    def test_basic_separation(self):
        data = {
            "note": {
                "field_names": [
                    "id",
                    "report_id",
                    "note_title",
                    "accounting_policies",
                    "rate_explained",
                    "is_minimis_rate_used",
                    "content",
                    "contains_chart_or_table",
                ],
                "entries": [
                    [1, "rpt1", "note1", "policy", "rate", "N", "content1", "Y"],
                    [2, "rpt1", "note2", "policy", "rate", "N", "content2", "N"],
                ],
            }
        }
        expected_output = {
            "note": {
                "field_names": [
                    "id",
                    "report_id",
                    "note_title",
                    "content",
                    "contains_chart_or_table",
                ],
                "entries": [
                    [1, "rpt1", "note1", "content1", "Y"],
                    [2, "rpt1", "note2", "content2", "N"],
                ],
            },
            "note_coversheet": {
                "field_names": [
                    "report_id",
                    "accounting_policies",
                    "rate_explained",
                    "is_minimis_rate_used",
                ],
                "entries": [["rpt1", "policy", "rate", "N"]],
            },
        }
        result = separate_notes_single_fields_from_array_fields(data)
        self.assertEqual(result, expected_output)

    def test_missing_section(self):
        data = {}
        result = separate_notes_single_fields_from_array_fields(data)
        self.assertEqual(result, {})

    def test_empty_entries(self):
        data = {
            "note": {
                "field_names": [
                    "report_id",
                    "accounting_policies",
                    "rate_explained",
                    "is_minimis_rate_used",
                    "other_info",
                ],
                "entries": [],
            }
        }
        expected_output = data  # Expect no change since there are no entries to process
        result = separate_notes_single_fields_from_array_fields(data)
        self.assertEqual(result, expected_output)


class ProcessUnifiedResultsTests(TestCase):
    def test_findings_without_reference_numbers_are_excluded(self):
        """Findings without reference numbers should not appear in reports."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_unified_results,
        )

        general = baker.make(General)

        bake_unified(
            general,
            [baker.make(Finding, report_id=general, reference_number="")],
        )
        bake_unified(
            general,
            [baker.make(Finding, report_id=general, reference_number="2024-001")],
        )

        names = {"finding"}
        data = initialize_data_structure(names)

        process_unified_results(
            [general.report_id],
            names,
            data,
            False,
            [],
        )

        self.assertEqual(len(data["finding"]["entries"]), 1)

        reference_index = data["finding"]["field_names"].index("reference_number")

        self.assertEqual(
            data["finding"]["entries"][0][reference_index],
            "2024-001",
        )

    @patch("dissemination.summary_reports.Unified")
    def test_findings_without_award_references_are_excluded(self, mock_unified):
        """Findings without award references should be excluded."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_unified_results,
        )

        report_id = "2024-06-GSAFAC-0000000001"
        names = {"finding"}
        data = initialize_data_structure(names)

        field_names = data["finding"]["field_names"]

        def make_finding(award_reference):
            fields = {name: None for name in field_names}
            fields.update(
                report_id=report_id,
                award_reference=award_reference,
                reference_number="2024-001",
                passthrough_name=None,
            )
            return SimpleNamespace(**fields)

        rows = [
            make_finding(None),
            make_finding(""),
            make_finding("AWARD-1"),
        ]

        mock_unified.objects.all.return_value.filter.return_value = rows

        process_unified_results([report_id], names, data, False, [])

        self.assertEqual(len(data["finding"]["entries"]), 1)

        award_index = field_names.index("award_reference")
        self.assertEqual(
            data["finding"]["entries"][0][award_index],
            "AWARD-1",
        )

    @patch("dissemination.summary_reports.Unified")
    def test_duplicate_general_and_federal_award_records(self, mock_unified):
        """General and federal award rows should not be duplicated."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_unified_results,
        )

        report_id = "2024-06-GSAFAC-0000000001"
        names = {"general", "federalaward"}
        data = initialize_data_structure(names)

        field_names = set(
            data["general"]["field_names"] + data["federalaward"]["field_names"]
        )

        def make_row(award_reference):
            fields = {name: None for name in field_names}
            fields.update(
                report_id=report_id,
                award_reference=award_reference,
                reference_number=None,
                passthrough_name=None,
            )
            return SimpleNamespace(**fields)

        rows = [
            make_row("AWARD-1"),
            make_row("AWARD-1"),
            make_row("AWARD-2"),
        ]

        mock_unified.objects.all.return_value.filter.return_value = rows

        process_unified_results([report_id], names, data, False, [])

        self.assertEqual(len(data["general"]["entries"]), 1)
        self.assertEqual(len(data["federalaward"]["entries"]), 2)

        award_index = data["federalaward"]["field_names"].index("award_reference")

        awards = [row[award_index] for row in data["federalaward"]["entries"]]

        self.assertCountEqual(
            awards,
            ["AWARD-1", "AWARD-2"],
        )

    @patch("dissemination.summary_reports.Unified")
    def test_empty_unified_results(self, mock_unified):
        """No Unified records should produce empty entries."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_unified_results,
        )

        report_id = "2024-06-GSAFAC-0000000001"
        names = {
            "general",
            "federalaward",
            "finding",
            "passthrough",
        }

        data = initialize_data_structure(names)

        mock_unified.objects.all.return_value.filter.return_value = []

        process_unified_results([report_id], names, data, False, [])

        for name in names:
            with self.subTest(model_name=name):
                self.assertEqual(data[name]["entries"], [])

    @patch("dissemination.summary_reports.Unified")
    def test_passthrough_without_name_is_excluded(self, mock_unified):
        """Passthrough rows without names should be excluded."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_unified_results,
        )

        report_id = "2024-06-GSAFAC-0000000001"
        names = {"passthrough"}
        data = initialize_data_structure(names)

        field_names = data["passthrough"]["field_names"]

        def make_passthrough(name):
            fields = {field: None for field in field_names}
            fields.update(
                report_id=report_id,
                award_reference="AWARD-1",
                reference_number=None,
                passthrough_name=name,
            )
            return SimpleNamespace(**fields)

        rows = [
            make_passthrough(None),
            make_passthrough("Test Organization"),
        ]

        mock_unified.objects.all.return_value.filter.return_value = rows

        process_unified_results([report_id], names, data, False, [])

        self.assertEqual(len(data["passthrough"]["entries"]), 1)

        name_index = field_names.index("passthrough_name")
        self.assertEqual(
            data["passthrough"]["entries"][0][name_index],
            "Test Organization",
        )


class ProcessNonUnifiedResultsTests(SimpleTestCase):
    @patch("dissemination.summary_reports._get_model_by_name")
    def test_excludes_private_tribal_records_without_permission(self, mock_get_model):
        """Restricted tribal records should be excluded without permission."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_non_unified_results,
        )

        public_id = "2024-06-GSAFAC-0000000001"
        tribal_id = "2024-06-GSAFAC-0000000002"

        names = {"findingtext"}
        data = initialize_data_structure(names)
        field_names = data["findingtext"]["field_names"]

        def make_record(report_id):
            fields = {name: None for name in field_names}
            fields.update(
                id=1,
                report_id=report_id,
                finding_ref_number="2024-001",
                finding_text="Test finding",
            )
            return SimpleNamespace(**fields)

        records = [
            make_record(public_id),
            make_record(tribal_id),
        ]

        mock_model = mock_get_model.return_value
        mock_model.objects.all.return_value.filter.return_value = records

        process_non_unified_results(
            [public_id, tribal_id],
            names,
            data,
            False,
            [tribal_id],
        )

        self.assertEqual(len(data["findingtext"]["entries"]), 1)

        report_id_index = field_names.index("report_id")

        self.assertEqual(
            data["findingtext"]["entries"][0][report_id_index],
            public_id,
        )

    @patch("dissemination.summary_reports._get_model_by_name")
    def test_includes_private_tribal_records_with_permission(self, mock_get_model):
        """Restricted tribal records should be included with permission."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_non_unified_results,
        )

        tribal_id = "2024-06-GSAFAC-0000000002"

        names = {"findingtext"}
        data = initialize_data_structure(names)
        field_names = data["findingtext"]["field_names"]

        fields = {name: None for name in field_names}
        fields.update(
            id=1,
            report_id=tribal_id,
            finding_ref_number="2024-001",
            finding_text="Private tribal finding",
        )

        record = SimpleNamespace(**fields)

        mock_model = mock_get_model.return_value
        mock_model.objects.all.return_value.filter.return_value = [record]

        process_non_unified_results(
            [tribal_id],
            names,
            data,
            True,
            [tribal_id],
        )

        self.assertEqual(len(data["findingtext"]["entries"]), 1)

        report_id_index = field_names.index("report_id")

        self.assertEqual(
            data["findingtext"]["entries"][0][report_id_index],
            tribal_id,
        )

    @patch("dissemination.summary_reports._get_model_by_name")
    def test_empty_results(self, mock_get_model):
        """No matching records should produce empty entries."""
        from dissemination.summary_reports import (
            initialize_data_structure,
            process_non_unified_results,
        )

        names = {"findingtext"}
        data = initialize_data_structure(names)

        mock_model = mock_get_model.return_value
        mock_model.objects.all.return_value.filter.return_value = []

        process_non_unified_results(
            ["2024-06-GSAFAC-0000000001"],
            names,
            data,
            False,
            [],
        )

        self.assertEqual(data["findingtext"]["entries"], [])
