local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';


local title_row = 3;

local single_cells = [
  Sheets.single_cell {
    title: 'Auditee UEI',
    range_name: 'auditee_uei',
    title_cell: 'A2',
    range_cell: 'B2',
    validation: SV.StringOfLengthTwelve,
    help: Help.uei,
  },
];

local open_ranges_defns = [
  [
    Sheets.open_range {
      title_cell: 'A3',
      width: 36,
      help: Help.uei,
    },
    SV.StringOfLengthTwelve,
    'Additional UEIs',
    'additional_uei',
  ]
];

local sheets = [
  {
    name: 'Form',
    single_cells: single_cells,
    open_ranges: Fun.make_open_ranges_with_column(title_row, open_ranges_defns),
    mergeable_cells: [
      [1, 2, 'A', 'B'],
      [3, Sheets.MAX_ROWS, 'A', 'B'],
    ],
    merged_unreachable: ['B'],
    header_inclusion: ['A1'],
  },
];

local workbook = {
  filename: 'additional-ueis-template.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
