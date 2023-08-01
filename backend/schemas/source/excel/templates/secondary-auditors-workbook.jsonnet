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
      width: 100,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Audit Firm/Organization Name',
    'secondary_auditor_name',
  ],
  [
    Sheets.open_range {
      title_cell: 'B1',
      width: 36,
      help: Help.ein,
    },
    SV.StringOfLengthNine,
    'Audit Firm or Organization EIN',
    'secondary_auditor_ein',
  ],
  [
    Sheets.open_range {
      title_cell: 'C1',
      width: 100,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Audit Firm/Organization Address (Number and Street)',
    'secondary_auditor_address_street',
  ],
  [
    Sheets.open_range {
      title_cell: 'D1',
      width: 100,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Audit Firm/Organization City',
    'secondary_auditor_address_city',
  ],
  [
    Sheets.open_range {
      title_cell: 'E1',
      width: 100,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Audit Firm/Organization State',
    'secondary_auditor_address_state',
  ],
  [
    Sheets.open_range {
      title_cell: 'F1',
      width: 36,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Audit Firm/Organization ZIP',
    'secondary_auditor_address_zipcode',
  ],
  [
    Sheets.open_range {
      title_cell: 'G1',
      width: 36,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Contact Name',
    'secondary_auditor_contact_name',
  ],
  [
    Sheets.open_range {
      title_cell: 'H1',
      width: 36,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Contact Title',
    'secondary_auditor_contact_title',
  ],
  [
    Sheets.open_range {
      title_cell: 'I1',
      width: 36,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Contact Phone Number',
    'secondary_auditor_contact_phone',
  ],
  [
    Sheets.open_range {
      title_cell: 'J1',
      width: 36,
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Contact E-mail',
    'secondary_auditor_contact_email',
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
  filename: 'secondary-auditors-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
