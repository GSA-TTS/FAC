local Base = import '../../base/Base.libsonnet';
local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local awardSheet = 'Form';
local ueiSheet = 'UEI';
local clusterSheet = 'Clusters';
local programSheet = 'FederalPrograms';
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
  Sheets.single_cell {
    title: 'Total amount expended',
    range_name: 'total_amount_expended',
    title_cell: 'B1',
    range_cell: 'B2',
    formula: "=SUM('" + awardSheet + "'!FIRSTCELLREF:LASTCELLREF)",
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
    Sheets.open_range {
      help: Help.unknown,
    },
    SV.NoValidation,
    'Additional Award Identification',
    'additional_award_identification',
  ],
  [
    Sheets.open_range {
      width: 48,
      help: Help.federal_program_name,
    },
    SV.RangeLookupValidation {
      sheet: programSheet,
      lookup_range: 'federal_program_name_lookup',
    },
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
      width: 48,
      help: Help.cluster_name,
    },
    SV.RangeLookupValidation {
      sheet: clusterSheet,
      lookup_range: 'cluster_name_lookup',
    },
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
    SV.YoNValidation,
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
    name: awardSheet,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
  },
  {
    name: ueiSheet,
    single_cells: single_cells,
    header_height: 100,
  },
  {
    name: clusterSheet,
    text_ranges: [
      {
        // Make this look like an open range
        type: 'text_range',
        title: 'Cluster Names',
        title_cell: 'A1',
        range_name: 'cluster_name_lookup',
        contents: Base.Compound.ClusterName,
        validation: SV.LookupValidation {
          lookup_range: 'cluster_name_lookup',
        },
      },
    ],
  },
  {
    name: programSheet,
    text_ranges: [
      {
        // Make this look like an open range
        type: 'text_range',
        title: 'Federal Program Names',
        title_cell: 'A1',
        range_name: 'federal_program_name_lookup',
        contents: Base.Compound.FederalProgramNames,
        validation: SV.LookupValidation {
          lookup_range: 'federal_prorgam_name_lookup',
        },
      },
      {
        // Make this look like an open range
        type: 'text_range',
        title: 'Program Numbers',
        title_cell: 'B1',
        range_name: 'aln_lookup',
        contents: Base.Compound.AllALNNumbers,
        validation: SV.LookupValidation {
          lookup_range: 'aln_lookup',
        },
      },
    ],
  },

];

local workbook = {
  filename: 'federal-awards-expended-template.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
