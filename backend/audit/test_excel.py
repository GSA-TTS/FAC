from django.test import SimpleTestCase
from openpyxl import load_workbook
from openpyxl.cell import Cell

from audit.excel import (
    extract_federal_awards,
    federal_awards_mapping_single,
    federal_awards_mapping_column,
)
from audit.validators import validate_federal_award_json


FEDERAL_AWARDS_TEMPLATE = "excel_templates/FederalAwardsExpendedTemplateUG2019.xlsx"

FEDERAL_AWARDS_ENTRY_FIXTURES = [
    {
        "amount_expended": 100,
        "cluster_name": "N/A",
        "direct_award": "N",
        "direct_award_pass_through_entity_name": "A|B",
        "direct_award_pass_through_entity_id": "1|2",
        "federal_award_passed_to_subrecipients": "N",
        "federal_award_passed_to_subrecipients_amount": 0,
        "federal_program_name": "program name",
        "loan_balance_at_audit_period_end": 0,
        "loan_or_loan_guarantee": "N",
        "major_program": "Y",
        "major_program_audit_report_type": "U",
        "number_of_audit_findings": 0,
        "program_number": "10.001",
        "state_cluster_name": "",
    },
    {
        "amount_expended": 100,
        "cluster_name": "N/A",
        "direct_award": "N",
        "direct_award_pass_through_entity_name": "C|D",
        "direct_award_pass_through_entity_id": "3|4",
        "federal_award_passed_to_subrecipients": "N",
        "federal_award_passed_to_subrecipients_amount": 0,
        "federal_program_name": "program name",
        "loan_balance_at_audit_period_end": 0,
        "loan_or_loan_guarantee": "N",
        "major_program": "Y",
        "major_program_audit_report_type": "U",
        "number_of_audit_findings": 0,
        "program_number": "10.002",
        "state_cluster_name": "",
    },
]


def _set_by_name(workbook, name, value, row_offset=0):
    definition = workbook.defined_names[name]

    sheet_title, cell_coord = next(definition.destinations)

    sheet = workbook[sheet_title]
    cell_range = sheet[cell_coord]

    if isinstance(cell_range, Cell):
        cell_range.value = value
    else:
        cell_range[row_offset][0].value = value


def _add_federal_award_entry(workbook, row_offset, entry):
    for key, value in entry.items():
        _set_by_name(workbook, key, value, row_offset)


class FederalAwardsExcelTests(SimpleTestCase):
    def test_template_has_named_ranges(self):
        """Test that the FederalAwardsExpended Excel template contains the expected named ranges"""
        workbook = load_workbook(FEDERAL_AWARDS_TEMPLATE, data_only=True)

        for name in federal_awards_mapping_single.keys():
            self.assertIsNotNone(workbook.defined_names[name])

        for name in federal_awards_mapping_column:
            self.assertIsNotNone(workbook.defined_names[name])

    def test_empty_template(self):
        """Test that extraction and validation succeed against the blank template"""
        federal_awards = extract_federal_awards(FEDERAL_AWARDS_TEMPLATE)

        validate_federal_award_json(federal_awards)

    def test_with_single_federal_awards_entry(self):
        """Test that extraction and validaiton succeed when there is a single federal awards entry"""
        workbook = load_workbook(FEDERAL_AWARDS_TEMPLATE, data_only=True)

        _set_by_name(workbook, "auditee_ein", "123456789")
        _set_by_name(workbook, "total_amount_expended", 100)
        _add_federal_award_entry(workbook, 0, FEDERAL_AWARDS_ENTRY_FIXTURES[0])

        federal_awards = extract_federal_awards(workbook)

        validate_federal_award_json(federal_awards)

    def test_with_multiple_federal_awards_entries(self):
        """Test that extraction and validaiton succeed when there are multiple federal awards entries"""
        workbook = load_workbook(FEDERAL_AWARDS_TEMPLATE, data_only=True)

        _set_by_name(workbook, "auditee_ein", "123456789")
        _set_by_name(workbook, "total_amount_expended", 200)
        for index, entry in enumerate(FEDERAL_AWARDS_ENTRY_FIXTURES):
            _add_federal_award_entry(workbook, index, entry)

        federal_awards = extract_federal_awards(workbook)

        validate_federal_award_json(federal_awards)
