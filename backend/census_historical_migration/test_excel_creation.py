from census_historical_migration.workbooklib.excel_creation import (
    set_range,
)

from django.test import TestCase
from openpyxl import Workbook
from openpyxl.utils import quote_sheetname, absolute_coordinate
from openpyxl.workbook.defined_name import DefinedName


class ExcelCreationTests(TestCase):
    range_name, start_val, end_val, cell = "my_range", "foo", "bar", "A6"


    def init_named_range(self, coord):
        wb = Workbook()
        ws = wb.active

        # Create named range
        ref = f"{quote_sheetname(ws.title)}!{absolute_coordinate(coord)}"
        defn = DefinedName(self.range_name, attr_text=ref)
        wb.defined_names.add(defn)

        return wb


    def test_set_range_standard(self):
        """
        Standard use case
        """
        wb = self.init_named_range('A6')
        ws = wb.active

        ws.cell(row=6, column=1, value='foo')
        self.assertEqual(ws['A6'].value, 'foo')

        set_range(wb, self.range_name, ['bar'])
        self.assertEqual(ws['A6'].value, 'bar')


    def test_set_range_default(self):
        """
        Using a default value
        """
        wb = self.init_named_range('A6')
        ws = wb.active

        ws.cell(row=6, column=1, value='foo')
        self.assertEqual(ws['A6'].value, 'foo')

        set_range(wb, self.range_name, [None], default='bar')
        self.assertEqual(ws['A6'].value, 'bar')


    def test_set_range_conversion(self):
        """
        Applies given conversion function
        """
        wb = self.init_named_range('A6')
        ws = wb.active

        ws.cell(row=6, column=1, value='foo')
        self.assertEqual(ws['A6'].value, 'foo')

        set_range(wb, self.range_name, ['1'], None, int)
        self.assertEqual(ws['A6'].value, 1) # str -> int


    def test_set_range_multiple_values(self):
        """
        Setting multiple values
        """
        wb = self.init_named_range('A1:A2')
        ws = wb.active

        ws.cell(row=1, column=1, value=0)
        self.assertEqual(ws['A1'].value, 0)

        ws.cell(row=2, column=1, value=0)
        self.assertEqual(ws['A2'].value, 0)

        set_range(wb, self.range_name, ['1', '2'])
        self.assertEqual(ws['A1'].value, '1')
        self.assertEqual(ws['A2'].value, '2')


    def test_set_range_fewer_values(self):
        """
        Number of values is less than the range size
        """
        wb = self.init_named_range('A1:A2')
        ws = wb.active

        ws.cell(row=1, column=1, value='foo')
        self.assertEqual(ws['A1'].value, 'foo')

        ws.cell(row=2, column=1, value='foo')
        self.assertEqual(ws['A2'].value, 'foo')

        set_range(wb, self.range_name, ['bar'])
        self.assertEqual(ws['A1'].value, 'bar') # New value
        self.assertEqual(ws['A2'].value, 'foo') # Unchanged
