local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local textSheet = 'Form';
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
    width: 80,
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
    value: Sheets.WORKBOOKS_VERSION,
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
    value: Sheets.section_names.AUDIT_FINDINGS_TEXT,
    help: Help.wrong_workbook_template,
    validation: SV.NoValidation,
  },
  Sheets.single_cell {
    keep_locked: true,
    title: 'Instructions',
    range_name: 'instructions_name',
    width: 48,
    title_cell: 'A4',
    range_cell: 'B4',
    value: 'https://www.fac.gov/audit-resources/sf-sac/federal-awards-audit-findings-text/',
    help: Help.wrong_workbook_template,
    validation: SV.NoValidation,
  },
  Sheets.single_cell {
    title: 'Auditee UEI:',
    range_name: 'auditee_uei',
    width: 48,
    title_cell: 'A5',
    range_cell: 'B5',
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
  [
    Sheets.open_range {
      title_cell: 'D1',
      width: 28,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Known Questioned Costs Dollars Amount (OPTIONAL)',
    'known_qc_amount',
  ],
  [
    Sheets.open_range {
      title_cell: 'E1',
      width: 28,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Likely Questioned Costs Dollars Amount (OPTIONAL)',
    'likely_qc_amount',
  ],
  [
    Sheets.open_range {
      title_cell: 'F1',
      width: 60,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Explanation If Questioned Costs Amount is Undetermined (OPTIONAL)',
    'undetermined_qc_explanation',
  ],
  [
    Sheets.open_range {
      title_cell: 'G1',
      width: 48,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Criteria (OPTIONAL)',
    'criteria',
  ],
  [
    Sheets.open_range {
      title_cell: 'H1',
      width: 48,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Condition (OPTIONAL)',
    'condition',
  ],
  [
    Sheets.open_range {
      title_cell: 'I1',
      width: 48,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Cause (OPTIONAL)',
    'cause',
  ],
  [
    Sheets.open_range {
      title_cell: 'J1',
      width: 48,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Effect (OPTIONAL)',
    'effect',
  ],
  [
    Sheets.open_range {
      title_cell: 'K1',
      width: 48,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Recommendation (OPTIONAL)',
    'recommendation',
  ],
  [
    Sheets.open_range {
      title_cell: 'L1',
      width: 48,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Response (OPTIONAL)',
    'response',
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
    name: textSheet,
    open_ranges: Fun.make_open_ranges_with_column(title_row, open_ranges_defns),
    header_height: 48,
    row_height: 36,
    hide_col_from: 13,
  },
];

local workbook = {
  filename: 'audit-findings-text-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
