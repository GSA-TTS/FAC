from census_historical_migration.workbooklib.excel_creation_utils import (
    set_range,
)

from django.test import TestCase
from openpyxl import Workbook
from openpyxl.utils import quote_sheetname, absolute_coordinate
from openpyxl.workbook.defined_name import DefinedName


class ExcelCreationTests(TestCase):
    range_name, start_val, end_val, cell = "my_range", "foo", "bar", "A6"

    def test_set_range(self):
        """
        Standard use case
        """
        wb = Workbook()
        ws = wb.active

        # Create named range
        ref = f"{quote_sheetname(ws.title)}!{absolute_coordinate(self.cell)}"
        defn = DefinedName(self.range_name, attr_text=ref)
        wb.defined_names.add(defn)

        ws.cell(row=6, column=1, value=self.start_val)
        self.assertEqual(ws[self.cell].value, self.start_val)

        set_range(wb, self.range_name, [self.end_val])
        self.assertEqual(ws[self.cell].value, self.end_val)
