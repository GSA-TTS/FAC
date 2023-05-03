local Fun = import 'Functions.libsonnet';
local Base = import '../../../schemas/sources/Base.libsonnet';
local Requiremnt = import '../../../schemas/sources/FindingsUniformGuidance.libsonnet';

local FAPPrefixValidation = {
    type: "list",
    allow_blank: "False",
    formula1: "\"" + Fun.make_aln_prefixes(Base.Enum.ALNPrefixes.enum) + "\"",
    custom_error: "The Federal Agency Prefix you entered is not recognized",
    custom_title: "Unknown ALN Prefix"
};

local YoNValidation = {
    type: "list",
    allow_blank: "False",
    formula1: "\"Y,N\"",
    custom_error: "Must be 'Y' or 'N'",
    custom_title: "Y/N"
};

// FIRSTCELLREF is magic, and gets replaced with the top
// of the relevant named range. It uses a relative row reference,
// so that it applies to every cell in the range.

// "type" is required; everything else is optional
local PositiveNumberValidation = {
    type: "custom",
    // Is it a number, and is the number either zero or greater than zero?
    formula1: "=AND(ISNUMBER(FIRSTCELLREF),OR(SIGN(FIRSTCELLREF)=0,SIGN(FIRSTCELLREF)=1))",
    custom_error: "This cell must be a positive number",
    custom_title: "Positive numbers"
};

local StringOfLengthThree = {
    type: "textLength",
    operator: "equal",
    formula1: 3,
    custom_error: "Expecting something with only three characters",
    custom_title: "Must be length of 3"
};

// local ComplianceRequirementValidation = {
//     type: "list",
//     allow_blank: "False",
//     enum: Requiremnt.ComplianceRequirement.ComplianceRequirement.enum,
//     custom_error: "Expecting a valid combination of the letters: A,B,C,E,F,G,H,I,J,L,M,N,P",
//     custom_title: "Compliance requirement"
// };

{
    FAPPrefixValidation: FAPPrefixValidation,
    PositiveNumberValidation: PositiveNumberValidation,
    StringOfLengthThree: StringOfLengthThree,
    YoNValidation: YoNValidation,
//    ComplianceRequirementValidation: ComplianceRequirementValidation
}