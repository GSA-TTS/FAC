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

local open_range_w12 = Sheets.open_range {
  width: 12,
};

local open_range_w24 = Sheets.open_range {
  width: 24,
};

local open_range_w20 = Sheets.open_range {
  width: 20,
};

local open_range_w48 = Sheets.open_range {
  width: 48,
};

local y_or_n_range_w16 = Sheets.y_or_n_range {
  width: 16,
};

local y_or_n_range_w16_with_formula = Sheets.y_or_n_range {
  width: 16,
  formula: '=IF(OR(G{0}="", H{0}="", I{0}="", J{0}="", K{0}=""), "", IF(OR(AND(G{0}="Y", H{0}="N", I{0}="N", J{0}="N", K{0}="N"), AND(G{0}="Y", H{0}="N", I{0}="Y", J{0}="N", K{0}="N"), AND(G{0}="Y", H{0}="N", I{0}="N", J{0}="Y", K{0}="N"), AND(G{0}="N", H{0}="Y", I{0}="N", J{0}="N", K{0}="N"), AND(G{0}="N", H{0}="Y", I{0}="Y", J{0}="N", K{0}="N"), AND(G{0}="N", H{0}="Y", I{0}="N", J{0}="Y", K{0}="N"), AND(G{0}="N", H{0}="N", I{0}="Y", J{0}="N", K{0}="N"), AND(G{0}="N", H{0}="N", I{0}="N", J{0}="Y", K{0}="N"), AND(G{0}="N", H{0}="N", I{0}="N", J{0}="N", K{0}="Y")), "Y", "N"))',
};

local y_or_n_range_w12 = Sheets.y_or_n_range {
  width: 12,
};

local open_ranges_defns = [
  [
    open_range_w12 {
      help: Help.aln_prefix,
    },
    SV.FAPPrefixValidation,
    'Federal Agency Prefix',
    'federal_agency_prefix',
  ],
  [
    open_range_w12 {
      help: Help.aln_extension,
    },
    SV.StringOfLengthThree,
    'CFDA Three Digit Extension',
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
    open_range_w48 {
      help: Help.plain_text,
    },
    SV.NoValidation,
    'Federal Program Name',
    'program_name',
  ],
  [
    Sheets.open_range {
      help: Help.reference_number,
    },
    SV.ReferenceNumberValidation,
    'Audit Finding Reference Number',
    'reference_number',
  ],
  [
    open_range_w20 {
      help: Help.unknown,
    },
    SV.ComplianceRequirementValidation,
    'Type(s) of Compliance Requirement(s)',
    'compliance_requirement',
  ],
  [
    y_or_n_range_w12 {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Modified Opinion',
    'modified_opinion',
  ],
  [
    y_or_n_range_w12 {
      help: Help.unknown,
    },
    SV.YoNValidation,
    'Other Matters',
    'other_matters',
  ],
  [
    y_or_n_range_w12 {
      help: Help.unknown,
    },
    SV.YoNValidation,
    'Material Weakness',
    'material_weakness',
  ],
  [
    y_or_n_range_w12 {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Significant Deficiency',
    'significant_deficiency',
  ],
  [
    y_or_n_range_w12 {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Other Findings',
    'other_findings',
  ],
  [
    y_or_n_range_w12 {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Questioned Costs',
    'questioned_costs',
  ],
  [
    y_or_n_range_w12 {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Repeat Findings from Prior Year',
    'repeat_prior_reference',
  ],
  [
    open_range_w24 {
      help: Help.yorn,
    },
    SV.NoValidation,
    'If Repeat Finding, provide Prior Year Audit Finding Reference Number(s)',
    'prior_references',
  ],
  [
    y_or_n_range_w16_with_formula {
      help: Help.yorn,
    },
    SV.YoNValidation,
    'Is Findings Combination Valid? (Read Only - Please See Instructions tab)',
    'is_valid',
  ],
];

local sheets = [
  {
    name: 'Form',
    single_cells: single_cells,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
    mergeable_cells: [
      [1, 2, 'A', 'O'],
      [2, 3, 'C', 'O'],
    ],
    header_inclusion: ['A1', 'C2'],
  },
];

local workbook = {
  filename: 'findings-uniform-guidance-template.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
