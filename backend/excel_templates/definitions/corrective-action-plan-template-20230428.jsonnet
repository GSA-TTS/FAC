local Fun = import 'libs/Functions.libsonnet';
local SV = import 'libs/SheetValidations.libsonnet';
local Sheets = import 'libs/Sheets.libsonnet';


local single_cells = [
  Sheets.SingleCell {
    title: 'Auditee UEI',
    range_name: 'auditee_ein',
    title_cell: 'A2',
    range_cell: 'B2',
  },
];

local open_range_w36 = Sheets.OpenRange {
  title_cell: 'A3',
  width: 36,
};

local open_range_w100 = Sheets.OpenRange {
  title_cell: 'C3',
  width: 100,
};

local y_or_n_range_w36 = Sheets.YorNRange {
  title_cell: 'G3',
  width: 36,
};

local open_ranges_defns = [
  [open_range_w36, {}, 'Audit Finding Reference Number', 'reference_number'],
  [open_range_w100, {}, 'Planned Corrective Action', 'planned_action'],
  [y_or_n_range_w36, {}, 'Did Text Contain a Chart or Table?', 'contains_chart_or_table'],
];

local sheets = [
  {
    name: 'Form',
    single_cells: single_cells,
    open_ranges: Fun.make_open_ranges_with_column(3, open_ranges_defns),
    cells_to_merge: [
      [1, 2, 'A', 'H'],
      [2, 3, 'C', 'H'],
      [3, Sheets.MAX_ROWS, 'A', 'B'],
      [3, Sheets.MAX_ROWS, 'C', 'F'],
      [3, Sheets.MAX_ROWS, 'G', 'H'],
    ],
    need_header_cell_style: ['A1', 'C2'],
  },
];

local workbook = {
  filename: 'corrective-action-plan-template-20230428.xlsx',
  sheets: sheets,
};

{} + workbook
