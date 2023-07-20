local Base = import '../../base/Base.libsonnet';
local Requirement = import '../../sections/FindingsUniformGuidance.libsonnet';
local Fun = import 'Functions.libsonnet';

local FAPPrefixValidation = {
  type: 'list',
  allow_blank: 'False',
  formula1: '"' + Fun.make_aln_prefixes(Base.Enum.ALNPrefixes.enum) + '"',
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
  formula1: '"Y,N,Y&N"',
  custom_error: "Must be 'Y' or 'N' or 'Y&N'",
  custom_title: 'Y/N/Y&N',
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

local ReferenceNumberValidation = {
  type: 'custom',
  //It is neccessary to allow blank otherwise user cannot delete the value
  formula1: '=OR(ISBLANK(FIRSTCELLREF), AND(LEN(FIRSTCELLREF) = 8, LEFT(FIRSTCELLREF, 2) = "20", ISNUMBER(MID(FIRSTCELLREF, 3, 2) * 1), MID(FIRSTCELLREF, 5, 1) = "-", ISNUMBER(RIGHT(FIRSTCELLREF, 3) * 1)))',
  custom_error: 'Expecting a value in the format YYYY-NNN, where YYYY is a year and NNN a three digit number (e.g. 2023-001)',
  custom_title: 'Reference number',
};

local StringOfLengthThree = {
  type: 'textLength',
  operator: 'equal',
  formula1: 3,
  custom_error: 'Expecting something with only three characters',
  custom_title: 'Must be length of 3',
};

local StringOfLengthNine = {
  type: 'textLength',
  operator: 'equal',
  formula1: 9,
  custom_error: 'Expecting something with nine characters',
  custom_title: 'Must be length of 9',
};

local StringOfLengthTwelve = {
  type: 'textLength',
  operator: 'equal',
  formula1: 12,
  custom_error: 'Expecting something with only twelve characters',
  custom_title: 'Must be length of 12',
};

local LoanBalanceValidation = {
  type: 'custom',
  // FIXME MSHD: for improvement, will need to pull column refs from this formula and retrieve that dynamically.
  formula1: '=IF(L{0}="N",ISBLANK(M{0}),OR(M{0}="N/A",AND(ISNUMBER(M{0}),M{0}>=0)))',
  custom_error: 'Loan Balance must be blank if Loan Guarantee is "N". If Loan Guarantee is "Y", Loan Balance must be a positive number or "N/A".',
  custom_title: 'Loan Balance',
};

local AwardReferenceValidation = {
  type: 'custom',
  formula1: '=AND(LEN(FIRSTCELLREF)=10, LEFT(FIRSTCELLREF, 6)="AWARD-", ISNUMBER(VALUE(MID(FIRSTCELLREF, 7, 4))), NOT(FIRSTCELLREF="AWARD-0000"))',
  custom_error: 'The value should follow the pattern AWARD-#### (where #### is a four-digit number).',
  custom_title: 'Award Reference validation',
};

{
  NoValidation: { type: 'NOVALIDATION' },
  FAPPrefixValidation: FAPPrefixValidation,
  PositiveNumberValidation: PositiveNumberValidation,
  LookupValidation: LookupValidation,
  RangeLookupValidation: RangeLookupValidation,
  StringOfLengthThree: StringOfLengthThree,
  StringOfLengthNine: StringOfLengthNine,
  StringOfLengthTwelve: StringOfLengthTwelve,
  YoNValidation: YoNValidation,
  ReferenceNumberValidation: ReferenceNumberValidation,
  LoanBalanceValidation: LoanBalanceValidation,
  AuditReportTypeValidation(namedRange): {
    type: 'list',
    allow_blank: 'True', 
    formula1: '=IF(S{0}="Y",' + namedRange + ',"")', 
    custom_error: 'The Audit Report Type must be empty if Major Program is "N"',
    custom_title: 'Invalid Audit Report Type',
  },
  YoNoBValidation: YoNoBValidation,
  AwardReferenceValidation: AwardReferenceValidation,
}
