local Base = import '../../base/Base.libsonnet';
local Requirement = import '../../sections/FindingsUniformGuidance.libsonnet';
local Fun = import 'Functions.libsonnet';

local FAPPrefixValidation = {
  type: 'custom',
  allow_blank: 'False',
  formula1: '=AND(LEN(FIRSTCELLREF)=2, AND(ISNUMBER(VALUE(MID(FIRSTCELLREF, 1, 1))), ISNUMBER(VALUE(MID(FIRSTCELLREF, 2, 1)))))',
  custom_error: 'The Federal Agency Prefix you entered is not recognized',
  custom_title: 'Unknown ALN Prefix',
};

local YoNValidation = {
  type: 'list',
  allow_blank: 'False',
  formula1: '"Y,N"',
  custom_error: "Must be 'Y' or 'N'",
  custom_title: 'Y/N',
};
local YoNoBValidation = {
  type: 'list',
  allow_blank: 'False',
  formula1: '"Y,N,Both"',
  custom_error: "Must be 'Y' or 'N' or 'Both'",
  custom_title: 'Y/N/Both',
};
// FIRSTCELLREF is magic, and gets replaced with the top
// of the relevant named range. It uses a relative row reference,
// so that it applies to every cell in the range.

local LookupValidation = {
  type: 'lookup',
  formula1: '=NOT(ISERROR(MATCH(FIRSTCELLREF,LOOKUPRANGE,0)))',
  custom_error: "Not in the lookup list",
  custom_title: 'Lookup validation',
};

local RangeLookupValidation = {
  type: 'range_lookup',
  lookup_range: 'NOTAVALIDNAMEDRANGE',
  # formula1: 'NOTAVALIDFORMULA',
  custom_error: "Not in the lookup list",
  custom_title: 'Lookup validation',
};

// "type" is required; everything else is optional
local PositiveNumberValidation = {
  type: 'custom',
  // Is it a number, and is the number either zero or greater than zero?
  formula1: '=AND(ISNUMBER(FIRSTCELLREF),OR(SIGN(FIRSTCELLREF)=0,SIGN(FIRSTCELLREF)=1))',
  custom_error: 'This cell must be a positive number',
  custom_title: 'Positive numbers',
};

local NumberValidation = {
  type: 'custom',
  // Is it a number ?
  formula1: '=ISNUMBER(FIRSTCELLREF)',
  custom_error: 'This cell must be a number',
  custom_title: 'Numbers',
};

local ReferenceNumberValidation = {
  type: 'custom',
  //It is neccessary to allow blank otherwise user cannot delete the value
  formula1: '=OR(ISBLANK(FIRSTCELLREF), AND(LEN(FIRSTCELLREF) = 8, LEFT(FIRSTCELLREF, 2) = "20", (MID(FIRSTCELLREF, 3, 1) * 1) > 0, ISNUMBER(MID(FIRSTCELLREF, 3, 2) * 1), MID(FIRSTCELLREF, 5, 1) = "-", ISNUMBER(RIGHT(FIRSTCELLREF, 3) * 1)))',
  custom_error: 'Expecting a value in the format YYYY-NNN, where YYYY is a year after 2010 and NNN a three digit number (e.g. 2023-001)',
  custom_title: 'Reference number',
};

local StringOfSize(size) = {
    type: 'textLength',
    operator: 'equal',
    formula1: size,
    custom_error: 'Expecting something with ' + size + ' characters',
    custom_title: 'Must be length of ' + size,
};

local LoanBalanceValidation = {
  type: 'custom',
  // FIXME MSHD: for improvement, will need to pull column refs from this formula and retrieve that dynamically.
  formula1: '=IF(L{0}="N",ISBLANK(M{0}),OR(M{0}="N/A",AND(ISNUMBER(VALUE(M{0})),M{0}>=0)))',
  custom_error: 'Loan Balance must be blank if Loan Guarantee is "N". If Loan Guarantee is "Y", Loan Balance must be a positive number or "N/A".',
  custom_title: 'Loan Balance',
};

local AwardReferenceValidation = {
  type: 'custom',
  formula1: '=AND(LEN(FIRSTCELLREF)=11, LEFT(FIRSTCELLREF, 6)="AWARD-", ISNUMBER(VALUE(MID(FIRSTCELLREF, 7, 5))), NOT(FIRSTCELLREF="AWARD-00000"))',
  custom_error: 'The value should follow the pattern AWARD-##### (where ##### is a five-digit number).',
  custom_title: 'Award Reference validation',
};

{
  NoValidation: { type: 'NOVALIDATION' },
  FAPPrefixValidation: FAPPrefixValidation,
  PositiveNumberValidation: PositiveNumberValidation,
  NumberValidation: NumberValidation,
  LookupValidation: LookupValidation,
  RangeLookupValidation: RangeLookupValidation,
  StringOfLengthNine: StringOfSize(9),
  StringOfLengthTwelve: StringOfSize(12),
  YoNValidation: YoNValidation,
  ReferenceNumberValidation: ReferenceNumberValidation,
  LoanBalanceValidation: LoanBalanceValidation,
  // WARNING MCJ
  // These were expressed with a single `:`. I was getting errors.
  // I replaced the single with a `::`. There is a semantic difference.
  // (It means it is a hidden field.) I don't think we want functions
  // manifested in the JSON. They... shouldn't be, but it was popping up.
  AuditReportTypeValidation(namedRange) :: {
    type: 'list',
    allow_blank: 'True',
    formula1: '=IF(S{0}="Y",' + namedRange + ',"")',
    custom_error: 'The Audit Report Type must be empty if Major Program is "N"',
    custom_title: 'Invalid Audit Report Type',
  },
  FederalProgramNameValidation(sheetName) :: {
    type: 'list',
    formula1: '=Y{0}:Y{0}',
    errorStyle: 'warning',
    custom_error: 'If the Program Name was provided, please, do not change it unless necessary or unknown. ' +
                  'The Program Name must be under 300 characters. ' +
                  'If the drop-down menu is empty, you may need to enter an Agency Prefix ' +
                  'and ALN in columns B and C. ' +
                  'Continue?',
    custom_title: 'Unknown Federal Program Name',
  },
  YoNoBValidation: YoNoBValidation,
  AwardReferenceValidation: AwardReferenceValidation,
}
