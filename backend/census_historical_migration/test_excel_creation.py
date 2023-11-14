from census_historical_migration.workbooklib.excel_creation import (
    set_single_cell_range,
)
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from audit.fixtures.excel import FORM_SECTIONS

from django.test import TestCase  # noqa: F401
from openpyxl import Workbook
from openpyxl.utils import quote_sheetname, absolute_coordinate
from openpyxl.workbook.defined_name import DefinedName


class ExcelCreationTests(TestCase):
    def test_set_single_cell_range(self):
        """
        Standard use case
        """
        wb = Workbook()
        ws = wb.active
        start_val, end_val, cell = 'foo', 'bar', 'A6'
        ref = f"{quote_sheetname(ws.title)}!{absolute_coordinate(cell)}"
        defn = DefinedName("private_range", attr_text=ref)
        wb.defined_names.add(defn)

        ws.cell(row=6, column=1, value=start_val)
        self.assertEqual(ws[cell].value, start_val)

        set_single_cell_range(wb, "private_range", end_val)
        self.assertEqual(ws[cell].value, end_val)
