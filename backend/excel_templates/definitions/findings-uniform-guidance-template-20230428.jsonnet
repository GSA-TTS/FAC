local Fun = import 'libs/Functions.libsonnet';
local SV = import 'libs/SheetValidations.libsonnet';
local Sheets = import 'libs/Sheets.libsonnet';


local single_cells = [
  Sheets.single_cell {
    title: 'Auditee UEI',
    range_name: 'auditee_ein',
    title_cell: 'A2',
    range_cell: 'B2',
  },
];


local open_range_w24 = Sheets.open_range {
  width: 24,
};

local open_range_w20 = Sheets.open_range {
  width: 20,
};

local y_or_n_range_w16 = Sheets.y_or_n_range {
  width: 16,
};

local y_or_n_range_w12 = Sheets.open_range {
  width: 12,
};

local open_ranges_defns = [
  [Sheets.open_range_w12, SV.FAPPrefixValidation, 'Federal Agency Prefix', 'federal_agency_prefix'],
  [Sheets.open_range_w12, SV.StringOfLengthThree, 'CFDA Three Digit Extension', 'three_digit_extension'],
  [Sheets.open_range, {}, 'Additional Award Identification', 'additional_award_identification'],
  [Sheets.open_range_w48, {}, 'Federal Program Name', 'program_name'],
  [Sheets.open_range, {}, 'Audit Finding Reference Number', 'finding_reference_number'],
  [open_range_w20, {}, 'Type(s) of Compliance Requirement(s)', 'compliance_requirement'],
  [y_or_n_range_w12, SV.YoNValidation, 'Modified Opinion', 'modified_opinion'],
  [y_or_n_range_w12, SV.YoNValidation, 'Other Matters', 'other_matters'],
  [y_or_n_range_w12, SV.YoNValidation, 'Material Weakness', 'material_weakness'],
  [y_or_n_range_w12, SV.YoNValidation, 'Significant Deficiency', 'significant_deficiency'],
  [y_or_n_range_w12, SV.YoNValidation, 'Other Findings', 'other_findings'],
  [y_or_n_range_w12, SV.YoNValidation, 'Questioned Costs', 'questioned_costs'],
  [y_or_n_range_w12, SV.YoNValidation, 'Repeat Findings from Prior Year', 'repeat_prior_reference'],
  [open_range_w24, {}, 'If Repeat Finding, provide Prior Year Audit Finding Reference Number(s)', 'prior_references'],
  [y_or_n_range_w16, SV.YoNValidation, 'Is Findings Combination Valid? (Read Only - Please See Instructions tab)', 'is_valid'],
];

local sheets = [
  {
    name: 'Form',
    single_cells: single_cells,
    open_ranges: Fun.make_open_ranges(3, open_ranges_defns),
    cells_to_merge: [
      [1, 2, 'A', 'O'],
      [2, 3, 'C', 'O'],
    ],
    include_in_header: ['A1', 'C2'],
  },
];

local workbook = {
  filename: 'findings-uniform-guidance-template-20230428.xlsx',
  sheets: sheets,
};

{} + workbook
