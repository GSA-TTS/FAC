local Base = import '../../base/Base.libsonnet';
local Fun = import '../libs/Functions.libsonnet';
local Help = import '../libs/Help.libsonnet';
local SV = import '../libs/SheetValidations.libsonnet';
local Sheets = import '../libs/Sheets.libsonnet';
local findingSheet = 'Form';
local coverSheet = 'Coversheet';
local complianceRequirementTypeSheet = 'ComplianceRequirementTypes';
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
    width: 48,
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
    formula: '="' + Sheets.section_names.FEDERAL_AWARDS_AUDIT_FINDINGS + '"',
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
    name: coverSheet,
    meta_cells: meta_cells,
    single_cells: single_cells,
    header_height: 60,
    hide_col_from: 3,
  },
  {
    name: findingSheet,
    open_ranges: Fun.make_open_ranges(title_row, open_ranges_defns),
    hide_col_from: 13,
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
  filename: 'federal-awards-audit-findings-workbook.xlsx',
  sheets: sheets,
  title_row: title_row,
};

{} + workbook
