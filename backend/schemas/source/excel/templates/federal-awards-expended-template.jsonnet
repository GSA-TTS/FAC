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
  Sheets.single_cell {
    title: 'Total amount expended',
    range_name: 'total_amount_expended',
    title_cell: 'D2',
    range_cell: 'E2',
    formula: '=SUM(FIRSTCELLREF:LASTCELLREF)',
    width: 36,
    help: Help.positive_number,

  },
];

local open_ranges_defns = [
  [
    Sheets.open_range {
      width: 12,
      help: Help.aln_prefix,
    },
    SV.FAPPrefixValidation,
    'Federal Agency Prefix',
    'federal_agency_prefix',
  ],
  [
    Sheets.open_range {
      width: 12,
      help: Help.aln_extension,
    },
    SV.StringOfLengthThree,
    'ALN (CFDA) Three Digit Extension',
    'three_digit_extension',
  ],
  [
    Sheets.open_range,
    SV.NoValidation,
    'Additional Award Identification',
    'additional_award_identification',
  ],
  [
    Sheets.open_range {
      width: 48,
      help: Help.federal_program_name,
    },
    SV.NoValidation,
    'Federal Program Name',
    'program_name',
  ],
  [
    Sheets.open_range {
      help: Help.positive_number,
    },
    SV.PositiveNumberValidation,
    'Amount Expended',
    'amount_expended',
  ],
  [
    Sheets.open_range {
      help: Help.yorn,
    },
    SV.NoValidation,
    'Cluster Name',
    'cluster_name',
  ],
  [
    Sheets.open_range {
      help: Help.cluster_name,
    },
    SV.NoValidation,
    'If State Cluster, Enter State Cluster Name',
    'state_cluster_name',
  ],
  [
    Sheets.open_range {
      help: Help.other_cluster_name,
    },
    SV.NoValidation,
    'If Other Cluster, Enter Other Cluster Name',
    'other_cluster_name',
  ],
  // 20230525 HDMS FIXME: A formula to auto calculate federal_program_total in the excel is missing (see instructions in census template)!!!
  [
    Sheets.open_range {
      help: Help.positive_number,
    },
    SV.PositiveNumberValidation,
    'Federal Program Total',
    'federal_program_total',
  ],
  [
    Sheets.open_range {
      help: Help.positive_number,
    },
    SV.PositiveNumberValidation,
    'Cluster Total',
    'cluster_total',
  ],
  [
    Sheets.y_or_n_range {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Loan / Loan Guarantee',
    'is_guaranteed',
  ],
  [
    Sheets.open_range {
      help: Help.positive_number,
    },
    SV.NoValidation,
    'If yes (Loan/Loan Guarantee, End of Audit Period Outstanding Loan Balance)',
    'loan_balance_at_audit_period_end',
  ],
  [
    Sheets.y_or_n_range {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Direct Award',
    'is_direct',
  ],
  [
    Sheets.y_or_n_range {
      help: Help.plain_text,
    },
    SV.NoValidation,
    'If no (Direct Award), Name of Passthrough Entity',
    'passthrough_name',
  ],
  [
    Sheets.open_range {
      width: 18,
      help: Help.unknown,
    },
    SV.YoNValidation,
    'If no (Direct Award), Identifying Number Assigned by the Pass-through Entity, if assigned',
    'passthrough_identifying_number',
  ],
  [
    Sheets.y_or_n_range {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Federal Award Passed Through to Subrecipients',
    'is_passed',
  ],
  [
    Sheets.open_range {
      help: Help.positive_number,
    },
    SV.NoValidation,
    'If yes (Passed Through), Amount Passed Through to Subrecipients',
    'subrecipient_amount',
  ],
  [
    Sheets.y_or_n_range {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Major Program (MP)',
    'is_major',
  ],
  [
    Sheets.open_range {
      width: 12,
      help: Help.unknown,
    },
    SV.NoValidation,
    'If yes (MP), Type of Audit Report',
    'audit_report_type',
  ],
  [
    Sheets.open_range {
      width: 12,
      help: Help.positive_number,
    },
    SV.PositiveNumberValidation,
    'Number of Audit Findings',
    'number_of_audit_findings',
  ],
];

local sheets = [
  {
    name: 'Form',
    single_cells: single_cells,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
    mergeable_cells: [
      [1, 2, 'A', 'T'],
      [2, 3, 'F', 'T'],
    ],
    header_inclusion: ['A1', 'C2', 'F2'],
  },
];

local workbook = {
  filename: 'federal-awards-expended-template.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
