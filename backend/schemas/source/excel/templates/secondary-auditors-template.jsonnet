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
      width: 100,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Audit Firm/Organization Name',
    'auditor_name',
  ],
  [
    Sheets.open_range {
      title_cell: 'B3',
      width: 36,
      help: Help.ein,
    },
    SV.StringOfLengthNine,
    'Audit Firm/Organization EIN',
    'auditor_ein',
  ],
  [
    Sheets.open_range {
      title_cell: 'C3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Audit Firm/Organization Address (Number and Street)',
    'auditor_address'
  ],
  [
    Sheets.open_range {
      title_cell: 'D3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Audit Firm/Organization City',
    'auditor_city'
  ],
  [
    Sheets.open_range {
      title_cell: 'E3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Audit Firm/Organization State',
    'auditor_state'
  ],
  [
    Sheets.open_range {
      title_cell: 'F3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Audit Firm/Organization ZIP',
    'auditor_zip'
  ],
  [
    Sheets.open_range {
      title_cell: 'G3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Contact Name',
    'contact_name'
  ],
  [
    Sheets.open_range {
      title_cell: 'H3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Contact Title',
    'contact_title'
  ],
  [
    Sheets.open_range {
      title_cell: 'I3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Contact Phone Number',
    'contact_phone'
  ],
  [
    Sheets.open_range {
      title_cell: 'J3',
      width: 100,
      help: Help.plain_text
    },
    SV.NoValidation,
    'Contact E-mail',
    'contact_email'
  ],
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
  title_row: title_row,
};

{} + workbook
