local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local additionalUeiSheet = 'Form';
local ueiSheet = 'Auditee UEI';
local title_row = 1;

local single_cells = [
  Sheets.single_cell {
    title: 'Auditee UEI',
    range_name: 'auditee_uei',
    width: 36,
    title_cell: 'A1',
    range_cell: 'A2',
    validation: SV.StringOfLengthTwelve,
    format: 'text',
    help: Help.uei,
  },
];

local open_ranges_defns = [
  [
    Sheets.open_range {
      title_cell: 'A1',
      width: 36,
      format: 'text',
      help: Help.uei,
    },
    SV.StringOfLengthTwelve,
    'Additional UEIs',
    'additional_uei',
  ],
];

local sheets = [
  {
    name: additionalUeiSheet,
    open_ranges: Fun.make_open_ranges_with_column(title_row, open_ranges_defns),
    header_height: 48,
    hide_col_from: 2,
  },
  {
    name: ueiSheet,
    single_cells: single_cells,
    header_height: 48,
    hide_col_from: 2,
    //FIXME MSHD: commented this out until we figure out if it is needed
    //  hide_row_from: 3,
  },
];

local workbook = {
  filename: 'additional-ueis-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
