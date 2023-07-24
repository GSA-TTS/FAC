local Base = import '../../base/Base.libsonnet';
local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local findingSheet = 'Form';
local ueiSheet = 'UEI';
local complianceRequirementTypeSheet = 'ComplianceRequirementTypes';
local title_row = 1;

local single_cells = [
  Sheets.single_cell {
    title: 'Auditee UEI',
    range_name: 'auditee_uei',
    width: 36,
    title_cell: 'A1',
    range_cell: 'A2',
    validation: SV.StringOfLengthTwelve,
    format: 'text',
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

local y_or_n_range_w12 = Sheets.y_or_n_range {
  width: 12,
};

local open_ranges_defns = [
  [
    Sheets.open_range {
      width: 18,
      help: Help.award_reference,
    },
    SV.AwardReferenceValidation,
    'Award Reference',
    'award_reference',
  ],
  [
    Sheets.open_range {
      width: 18,
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
    SV.RangeLookupValidation {
      sheet: complianceRequirementTypeSheet,
      lookup_range: 'requirement_type_lookup',
      custom_error: 'Please enter a valid Type of Compliance Requirement. (One or more of ABCEFGHIJLMNP, in alphabetical order).',
    },
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
    y_or_n_range_w16 {
      keep_locked: true,
      formula: '=IF(OR(D{0}="", E{0}="", F{0}="", G{0}="", H{0}=""), "", IF(OR(AND(D{0}="Y", E{0}="N", F{0}="N", G{0}="N", H{0}="N"), AND(D{0}="Y", E{0}="N", F{0}="Y", G{0}="N", H{0}="N"), AND(D{0}="Y", E{0}="N", F{0}="N", G{0}="Y", H{0}="N"), AND(D{0}="N", E{0}="Y", F{0}="N", G{0}="N", H{0}="N"), AND(D{0}="N", E{0}="Y", F{0}="Y", G{0}="N", H{0}="N"), AND(D{0}="N", E{0}="Y", F{0}="N", G{0}="Y", H{0}="N"), AND(D{0}="N", E{0}="N", F{0}="Y", G{0}="N", H{0}="N"), AND(D{0}="N", E{0}="N", F{0}="N", G{0}="Y", H{0}="N"), AND(D{0}="N", E{0}="N", F{0}="N", G{0}="N", H{0}="Y")), "Y", "N"))',
      help: Help.yorn,
    },
    SV.YoNValidation,
    //FIXME MSHD: If we end up adding an instructions sheet, then we add back" - See Instructions tab" to the end of this string below
    'Is Findings Combination Valid? (Read Only)',
    'is_valid',
  ],
];

local sheets = [
  {
    name: findingSheet,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
    hide_col_from: 13,
  },
  {
    name: ueiSheet,
    single_cells: single_cells,
    header_height: 100,
    hide_col_from: 2,
    //FIXME MSHD: commented this out until we figure out if it is needed
    //hide_row_from: 3,
  },
  {
    name: complianceRequirementTypeSheet,
    text_ranges: [
      {
        type: 'text_range',
        title: 'Compliance Requirement types',
        title_cell: 'A1',
        range_name: 'requirement_type_lookup',
        last_range_cell: 'A8192',
        contents: Base.Compound.ComplianceRequirementTypes,
        validation: SV.LookupValidation {
          lookup_range: 'requirement_type_lookup',
        },
      },
    ],
  },
];

local workbook = {
  filename: 'findings-uniform-guidance-template.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
