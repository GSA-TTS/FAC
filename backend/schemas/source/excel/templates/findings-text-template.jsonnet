local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local textSheet = 'Form';
local ueiSheet = 'UEI';
local title_row = 1;

local single_cells = [
  Sheets.single_cell {
    title: 'Auditee UEI',
    range_name: 'auditee_uei',
    width: 36,
    title_cell: 'A1',
    range_cell: 'A2',
    validation: SV.StringOfLengthTwelve,
    help: Help.uei,
  },
];

local open_ranges_defns = [
  [
    Sheets.open_range {
      title_cell: 'A1',
      width: 36,
      help: Help.reference_number,
    },
    SV.ReferenceNumberValidation,
    'Audit Finding Reference Number',
    'reference_number',
  ],
  [
    Sheets.open_range {
      title_cell: 'B1',
      width: 100,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Text of the Audit Finding',
    'text_of_finding',
  ],
  [
    Sheets.y_or_n_range {
      title_cell: 'C1',
      width: 36,
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Did Text Contain a Chart or Table?',
    'contains_chart_or_table',
  ],
];

local sheets = [
  {
    name: textSheet,
    open_ranges: Fun.make_open_ranges_with_column(title_row, open_ranges_defns),
    header_height: 48,
  },
  {
    name: ueiSheet,
    single_cells: single_cells,
    header_height: 48,
  },
];

local workbook = {
  filename: 'findings-text-template.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
