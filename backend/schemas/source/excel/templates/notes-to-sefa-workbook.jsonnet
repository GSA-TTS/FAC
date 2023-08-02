local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local sefaMandatorySheet = 'MandatoryNotes';
local sefaAdditionalSheet = 'AdditionalNotes';
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
local other_single_cells = [
  Sheets.single_cell {
    title: 'Describe the significant accounting policies \nused in preparing the SEFA. (2 CFR 200.510(b)(6))',
    range_name: 'accounting_policies',
    width: 56,
    title_cell: 'A1',
    range_cell: 'A2',
    validation: SV.NoValidation,
    help: Help.plain_text,
  },
  Sheets.single_cell {
    title: 'Did the auditee use the de minimis cost rate? \n(2 CFR 200.414(f))',
    range_name: 'is_minimis_rate_used',
    width: 24,
    title_cell: 'B1',
    range_cell: 'B2',
    validation: SV.YoNoBValidation,
    help: Help.yorn,
  },
  Sheets.single_cell {
    title: 'Please explain',
    range_name: 'rate_explained',
    width: 56,
    title_cell: 'C1',
    range_cell: 'C2',
    validation: SV.NoValidation,
    help: Help.plain_text,
  },
];

local open_ranges_defns = [
  [
    Sheets.open_range {
      width: 36,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Note title',
    'note_title',
  ],
  [
    Sheets.open_range {
      width: 56,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Note content',
    'note_content',
  ],
  [
    Sheets.open_range {
      keep_locked: true,
      formula: '=IF(A{0}<>"", ROW()-1, "")',
      width: 18,
      help: Help.unknown,
    },
    SV.NoValidation,
    'Sequence number (Read Only)',
    'seq_number',
  ],
];

local sheets = [
  {
    name: sefaMandatorySheet,
    single_cells: other_single_cells,
    header_height: 100,
    hide_col_from: 4,
  },
  {
    name: sefaAdditionalSheet,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
    header_height: 100,
    hide_col_from: 3,
  },
  {
    name: ueiSheet,
    single_cells: single_cells,
    header_height: 100,
    hide_col_from: 2,
  },
];

local workbook = {
  filename: 'notes-to-sefa-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
