local Fun = import 'libs/Functions.libsonnet';
local SV = import 'libs/SheetValidations.libsonnet';
local Sheets = import 'libs/Sheets.libsonnet';

local title_row = 3;

local single_cells = [
  Sheets.single_cell {
    title: 'Auditee UEI',
    range_name: 'auditee_uei',
    title_cell: 'A2',
    range_cell: 'B2',
    validation: SV.StringOfLengthTwelve,
  },
];

local open_ranges_defns = [
  [Sheets.open_range_a3_w36, SV.ReferenceNumberValidation, 'Audit Finding Reference Number', 'reference_number'],
  [Sheets.open_range_c3_w100, {}, 'Planned Corrective Action', 'planned_action'],
  [Sheets.y_or_n_range_g3_w36, SV.YoNValidation, 'Did Text Contain a Chart or Table?', 'contains_chart_or_table'],
];

local sheets = [
  {
    name: 'Form',
    single_cells: single_cells,
    open_ranges: Fun.make_open_ranges_with_column(title_row, open_ranges_defns),
    mergeable_cells: [
      [1, 2, 'A', 'H'],
      [2, 3, 'C', 'H'],
      [3, Sheets.MAX_ROWS, 'A', 'B'],
      [3, Sheets.MAX_ROWS, 'C', 'F'],
      [3, Sheets.MAX_ROWS, 'G', 'H'],
    ],
    merged_unreachable: ['B', 'D', 'E', 'F', 'H'],
    header_inclusion: ['A1', 'C2'],
  },
];

local workbook = {
  filename: 'corrective-action-plan-template.xlsx',
  sheets: sheets,
  title_row:title_row,
};

{} + workbook
