local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local additionalUeiSheet = 'Form';
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
    title: 'This workbook contains two worksheets: a coversheet (this sheet) and a data entry sheet.\nBefore submitting, please make sure the fields below are filled out.',
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
    formula: '="' + Sheets.section_names.ADDITIONAL_UEIS + '"',
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
    name: coverSheet,
    meta_cells: meta_cells,
    single_cells: single_cells,
    header_height: 60,
    hide_col_from: 3,
    //FIXME MSHD: commented this out until we figure out if it is needed
    //  hide_row_from: 3,
  },
  {
    name: additionalUeiSheet,
    open_ranges: Fun.make_open_ranges_with_column(title_row, open_ranges_defns),
    header_height: 48,
    hide_col_from: 2,
  },
];

local workbook = {
  filename: 'additional-ueis-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
