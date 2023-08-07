local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local sefaMandatorySheet = 'MandatoryNotes';
local sefaAdditionalSheet = 'AdditionalNotes';
local coverSheet = 'Coversheet';
local title_row = 1;

local meta_cells = [
  Sheets.meta_cell {
    keep_locked: true,
    title: 'Federal Audit Clearinghouse\nfac.gov',
    title_cell: 'A1',
    help: Help.unknown,
  },
  Sheets.meta_cell {
    keep_locked: true,
    width: 48,
    title: 'This workbook contains two worksheets: a coversheet (this sheet) and a mandatory notes sheet.\nBefore submitting, please make sure the fields below are filled out.',
    title_cell: 'B1',
    help: Help.unknown,
  },
];

local single_cells = [
  Sheets.single_cell {
    keep_locked: true,
    title: 'Version',
    range_name: 'version',
    width: 48,
    title_cell: 'A2',
    range_cell: 'B2',
    format: 'text',
    formula: '="' + Sheets.WORKBOOKS_VERSION + '"',
    help: Help.plain_text,
    validation: SV.NoValidation,
  },
  Sheets.single_cell {
    keep_locked: true,
    title: 'Section',
    range_name: 'section_name',
    width: 48,
    title_cell: 'A3',
    range_cell: 'B3',
    format: 'text',
    formula: '="' + Sheets.section_names.NOTES_TO_SEFA + '"',
    help: Help.plain_text,
    validation: SV.NoValidation,
  },
  Sheets.single_cell {
    title: 'Auditee UEI:',
    range_name: 'auditee_uei',
    width: 48,
    title_cell: 'A4',
    range_cell: 'B4',
    format: 'text',
    validation: SV.StringOfLengthTwelve,
    help: Help.uei,
  },
  Sheets.single_cell {
    title: 'Describe the significant accounting policies \nused in preparing the SEFA. (2 CFR 200.510(b)(6))',
    range_name: 'accounting_policies',
    width: 56,
    title_cell: 'A5',
    range_cell: 'B5',
    validation: SV.NoValidation,
    help: Help.plain_text,
  },
  Sheets.single_cell {
    title: 'Did the auditee use the de minimis cost rate? \n(2 CFR 200.414(f))',
    range_name: 'is_minimis_rate_used',
    width: 24,
    title_cell: 'A6',
    range_cell: 'B6',
    validation: SV.YoNoBValidation,
    help: Help.yorn,
  },
  Sheets.single_cell {
    title: 'Please explain',
    range_name: 'rate_explained',
    width: 56,
    title_cell: 'A7',
    range_cell: 'B7',
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
    name: coverSheet,
    meta_cells: meta_cells,
    single_cells: single_cells,
    header_height: 60,
    hide_col_from: 3,
  },
  {
    name: sefaAdditionalSheet,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
    header_height: 100,
    hide_col_from: 3,
  },
];

local workbook = {
  filename: 'notes-to-sefa-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
