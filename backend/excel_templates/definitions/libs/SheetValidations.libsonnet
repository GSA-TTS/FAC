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

local ReferenceNumberValidation = {
    type: "custom",
    //It is neccessary to allow blank otherwise user cannot delete the value
    formula1: "=OR(ISBLANK(FIRSTCELLREF), AND(LEN(FIRSTCELLREF) = 8, LEFT(FIRSTCELLREF, 2) = \"20\", ISNUMBER(MID(FIRSTCELLREF, 3, 2) * 1), MID(FIRSTCELLREF, 5, 1) = \"-\", ISNUMBER(RIGHT(FIRSTCELLREF, 3) * 1)))",
    custom_error: "Expecting a value in the format YYYY-NNN, where YYYY is a year and NNN a three digit number (e.g. 2023-001)",
    custom_title: "Reference number"
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
    ReferenceNumberValidation: ReferenceNumberValidation
//    ComplianceRequirementValidation: ComplianceRequirementValidation
}