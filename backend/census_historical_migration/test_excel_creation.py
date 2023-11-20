from census_historical_migration.workbooklib.excel_creation import (
    set_range,
)

from django.test import TestCase
from openpyxl import Workbook
from openpyxl.utils import quote_sheetname, absolute_coordinate
from openpyxl.workbook.defined_name import DefinedName


class ExcelCreationTests(TestCase):
    range_name = "my_range"


    def init_named_range(self, coord):
        """
        Create and return a workbook with a named range for the given coordinate
        """
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


    def test_set_range_multi_dests(self):
        """
        Error when multiple destinations found
        """
        wb = Workbook()
        ws = wb.active

        # Create named range with multiple destinations
        ref = \
            f"{quote_sheetname(ws.title)}!{absolute_coordinate('A6')}, \
              {quote_sheetname(ws.title)}!{absolute_coordinate('B6')}"
        defn = DefinedName(self.range_name, attr_text=ref)
        wb.defined_names.add(defn)

        self.assertEqual(len(list(wb.defined_names[self.range_name].destinations)), 2)
        self.assertRaises(ValueError, set_range, wb, self.range_name, ['bar'])


    def test_set_range_ws_missing(self):
        """
        Error when the named range isn't in the given WS
        """
        wb = Workbook()

        # Create named range with bad sheet title
        ref = f"{quote_sheetname('wrong name')}!{absolute_coordinate('A6')}"
        defn = DefinedName(self.range_name, attr_text=ref)
        wb.defined_names.add(defn)

        self.assertRaises(KeyError, set_range, wb, self.range_name, ['bar'])
