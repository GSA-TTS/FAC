local Fun = import 'libs/Functions.libsonnet';
local SV = import 'libs/SheetValidations.libsonnet';
local Sheets = import 'libs/Sheets.libsonnet';

local title_row = 3;

local single_cells = [
  Sheets.single_cell {
    title: 'Auditee UEI',
    range_name: 'auditee_uei',
    title_cell: 'A2',
    range_cell: 'B2',
    validation: SV.StringOfLengthTwelve,
  },
  Sheets.single_cell {
    title: 'Total amount expended',
    range_name: 'total_amount_expended',
    title_cell: 'D2',
    range_cell: 'E2',
    formula: '=SUM(FIRSTCELLREF:LASTCELLREF)',
    width: 36,
  },
];

local open_ranges_defns = [
  [Sheets.open_range {
    width: 12,
  }, SV.FAPPrefixValidation, 'Federal Agency Prefix', 'federal_agency_prefix'],
  [Sheets.open_range {
    width: 12,
  }, SV.StringOfLengthThree, 'CFDA Three Digit Extension', 'three_digit_extension'],
  [Sheets.open_range, {}, 'Additional Award Identification', 'additional_award_identification'],
  [Sheets.open_range {
    width: 48,
  }, {}, 'Federal Program Name', 'program_name'],
  [Sheets.open_range, SV.PositiveNumberValidation, 'Amount Expended', 'amount_expended'],
  [Sheets.open_range, {}, 'Cluster Name', 'cluster_name'],
  [Sheets.open_range, {}, 'If State Cluster, Enter State Cluster Name', 'state_cluster_name'],
  [Sheets.open_range, {}, 'If Other Cluster, Enter Other Cluster Name', 'other_cluster_name'],
  [Sheets.open_range, SV.PositiveNumberValidation, 'Federal Program Total', 'federal_program_total'],
  [Sheets.open_range, SV.PositiveNumberValidation, 'Cluster Total', 'cluster_total'],
  [Sheets.y_or_n_range, SV.YoNValidation, 'Loan / Loan Guarantee', 'is_guaranteed'],
  [Sheets.open_range, {}, 'If yes (Loan/Loan Guarantee, End of Audit Period Outstanding Loan Balance)', 'loan_balance_at_audit_period_end'],
  [Sheets.y_or_n_range, SV.YoNValidation, 'Direct Award', 'is_direct'],
  [Sheets.y_or_n_range, SV.YoNValidation, 'If no (Direct Award), Name of Passthrough Entity', 'passthrough_name'],
  [
    Sheets.open_range {
      width: 18,
    },
    {},
    'If no (Direct Award), Identifying Number Assigned by the Pass-through Entity, if assigned',
    'passthrough_identifying_number',
  ],
  [Sheets.y_or_n_range, SV.YoNValidation, 'Federal Award Passed Through to Subrecipients', 'is_passed'],
  [Sheets.open_range, {}, 'If yes (Passed Through), Amount Passed Through to Subrecipients', 'subrecipient_amount'],
  [Sheets.y_or_n_range, SV.YoNValidation, 'Major Program (MP)', 'is_major'],
  [Sheets.open_range {
    width: 12,
  }, {}, 'If yes (MP), Type of Audit Report', 'audit_report_type'],
  [Sheets.open_range {
    width: 12,
  }, SV.PositiveNumberValidation, 'Number of Audit Findings', 'number_of_audit_findings'],
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
