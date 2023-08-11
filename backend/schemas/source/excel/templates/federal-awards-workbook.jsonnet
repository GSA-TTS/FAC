local Base = import '../../base/Base.libsonnet';
local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local awardSheet = 'Form';
local coverSheet = 'Coversheet';
local clusterSheet = 'Clusters';
local programSheet = 'FederalPrograms';
local auditReportTypeSheet = 'AuditReportTypes';
local title_row = 1;
local amountExpendedNamedRange = 'amount_expended';
local cfdaKeyNamedRange = 'cfda_key';
local uniformOtherClusterNamedRange = 'uniform_other_cluster_name';
local uniformStateClusterNamedRange = 'uniform_state_cluster_name';
local clusterNamedRange = 'cluster_name';
local auditReportTypeLookupNamedRange = 'audit_report_type_lookup';
local alnLookUpNamedRange = 'aln_lookup';
local federalProgramNameLookupNamedRange = 'federal_program_name_lookup';

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
    title: 'This workbook contains five worksheets: the first two are editable while the last three are read-only.\nBefore submitting, please make sure the fields below are filled out.',
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
    formula: '="' + Sheets.section_names.FEDERAL_AWARDS + '"',
    help: Help.wrong_workbook_template,
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
    keep_locked: true,
    title: 'Total amount expended',
    range_name: 'total_amount_expended',
    title_cell: 'A5',
    range_cell: 'B5',
    format: 'dollar',
    // FIXME MSHD: for improvement, will need to pull F from this formula and retrieve it dynamically.
    formula: "=SUM('" + awardSheet + "'!F$FIRSTROW:F$LASTROW)",
    width: 36,
    help: Help.positive_number,
    validation: SV.PositiveNumberValidation,
  },
];

local open_ranges_defns = [
  [
    Sheets.open_range {
      keep_locked: true,
      formula: '=IF(B{0}<>"", "AWARD-"&TEXT(ROW()-1,"0000"), "")',
      width: 18,
      help: Help.award_reference,
    },
    SV.NoValidation,
    'Award Reference (Read Only)',
    'award_reference',
  ],
  [
    Sheets.open_range {
      format: 'text',
      width: 12,
      help: Help.aln_prefix,
    },
    SV.FAPPrefixValidation,
    'Federal Agency Prefix',
    'federal_agency_prefix',
  ],
  [
    Sheets.open_range {
      format: 'text',
      width: 12,
      help: Help.aln_extension,
    },
    SV.NoValidation,
    'ALN (CFDA) Three Digit Extension',
    'three_digit_extension',
  ],
  [
    Sheets.open_range {
      format: 'text',
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
    SV.FederalProgramNameValidation(programSheet),
    'Federal Program Name',
    'program_name',
  ],
  [
    Sheets.open_range {
      format: 'dollar',
      help: Help.positive_number,
    },
    SV.PositiveNumberValidation,
    'Amount Expended',
    amountExpendedNamedRange,
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
    clusterNamedRange,
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
  [
    Sheets.open_range {
      keep_locked: true,
      format: 'dollar',
      formula: '=SUMIFS(' + amountExpendedNamedRange + ',' + cfdaKeyNamedRange + ',V{0})',
      help: Help.positive_number,
    },
    SV.PositiveNumberValidation,
    'Federal Program Total',
    'federal_program_total',
  ],
  [
    Sheets.open_range {
      keep_locked: true,
      format: 'dollar',
      formula: '=IF(G{0}="' + Base.Const.OTHER_CLUSTER + '",SUMIFS(' + amountExpendedNamedRange + ',' + uniformOtherClusterNamedRange + ',X{0}), IF(AND(OR(G{0}="' + Base.Const.NA + '",G{0}=""),H{0}=""),0,IF(G{0}="' + Base.Const.STATE_CLUSTER + '",SUMIFS(' + amountExpendedNamedRange + ',' + uniformStateClusterNamedRange + ',W{0}),SUMIFS(' + amountExpendedNamedRange + ',' + clusterNamedRange + ',G{0}))))',
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
      format: 'dollar',
      help: Help.positive_number,
    },
    SV.LoanBalanceValidation,
    'If yes (Loan/Loan Guarantee), End of Audit Period Outstanding Loan Balance',
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
      format: 'text',
      help: Help.plain_text,
    },
    SV.NoValidation,
    'If no (Direct Award), Name of Passthrough Entity',
    'passthrough_name',
  ],
  [
    Sheets.open_range {
      format: 'text',
      width: 18,
      help: Help.unknown,
    },
    SV.NoValidation,
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
      format: 'dollar',
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
    SV.AuditReportTypeValidation(auditReportTypeLookupNamedRange),
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
  [
    Sheets.open_range {
      keep_locked: true,
      formula: '=IF(OR(B{0}="",C{0}),"",CONCATENATE(B{0},".",C{0}))',
      width: 12,
      format: 'text',
      help: Help.unknown,
    },
    SV.NoValidation,
    'CFDA_KEY (Read Only)',
    cfdaKeyNamedRange,
  ],
  [
    Sheets.open_range {
      keep_locked: true,
      formula: '=UPPER(TRIM(H{0}))',
      width: 24,
      help: Help.unknown,
    },
    SV.NoValidation,
    'UNIFORM STATE CLUSTER NAME (Read Only)',
    uniformStateClusterNamedRange,
  ],
  [
    Sheets.open_range {
      keep_locked: true,
      formula: '=UPPER(TRIM(I{0}))',
      width: 24,
      help: Help.unknown,
    },
    SV.NoValidation,
    'UNIFORM OTHER CLUSTER NAME (Read Only)',
    uniformOtherClusterNamedRange,
  ],
  [
    Sheets.open_range {
      keep_locked: true,
      formula: '=IF(V{0}<>"",IFERROR(INDEX(' + federalProgramNameLookupNamedRange + ',MATCH(V{0},' + alnLookUpNamedRange + ',0)),""),"")',
      width: 48,
      help: Help.unknown,
    },
    SV.NoValidation,
    'DEFAULT PROGRAM NAME (Read Only)',
    'default_program_name',
  ],
];

local sheets = [
  {
    name: coverSheet,
    meta_cells: meta_cells,
    single_cells: single_cells,
    header_height: 60,
    hide_col_from: 3,
    //  hide_row_from: 3,
  },
  {
    name: awardSheet,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
    hide_col_from: 22,
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
        contents: Base.Compound.ClusterNamesNAStateOther,
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
        range_name: federalProgramNameLookupNamedRange,
        contents: Base.Compound.FederalProgramNames,
        validation: SV.LookupValidation {
          lookup_range: federalProgramNameLookupNamedRange,
        },
      },
      {
        // Make this look like an open range
        type: 'text_range',
        title: 'Program Numbers',
        title_cell: 'B1',
        range_name: alnLookUpNamedRange,
        contents: Base.Compound.AllALNNumbers,
        validation: SV.LookupValidation {
          lookup_range: alnLookUpNamedRange,
        },
      },
    ],
  },
  {
    name: auditReportTypeSheet,
    text_ranges: [
      {
        type: 'text_range',
        title: 'Major Program Audit Report Type',
        title_cell: 'A1',
        range_name: auditReportTypeLookupNamedRange,
        last_range_cell: 'A5',
        contents: Base.Enum.MajorProgramAuditReportType,
        validation: SV.LookupValidation {
          lookup_range: auditReportTypeLookupNamedRange,
        },
      },
    ],
  },
];

local workbook = {
  filename: 'federal-awards-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
