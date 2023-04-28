local Sheets = import 'libs/Sheets.libsonnet';
local Fun = import 'libs/Functions.libsonnet';
local SV = import 'libs/SheetValidations.libsonnet';

local single_cells = [
    Sheets.SingleCell + {
        title: "Auditee UEI",
        range_name: "auditee_ein",
        title_cell: "A4",
        range_cell: "B4"
    },
    Sheets.SingleCell + {
        title: "Total amount expended",
        range_name: "total_amount_expended",
        title_cell: "D4",
        range_cell: "E4",
        validation: SV.PositiveNumberValidation,
        width: 36
    },
];

local open_ranges_defns = [
    [Sheets.OpenRange, SV.FAPPrefixValidation, "Federal Agency Prefix", "federal_agency_prefix"],
    [Sheets.OpenRange, SV.StringOfLengthThree, "CFDA Three Digit Extension", "three_digit_extension"],
    [Sheets.OpenRange, {}, "Additional Award Identification", "additional_award_identification"],
    [Sheets.OpenRange, {}, "Federal Program Name", "federal_program_name"],
    [Sheets.OpenRange, SV.PositiveNumberValidation, "Amount Expended", "amount_expended"],
    [Sheets.OpenRange, {}, "Cluster Name", "cluster_name"],
    [Sheets.OpenRange, {}, "If State Cluster, Enter State Cluster Name", "state_cluster_name"],
    [Sheets.OpenRange, {}, "If Other Cluster, Enter Other Cluster Name", "other_cluster_name"],
    [Sheets.OpenRange, {}, "Federal Program Total", "federal_program_total"],
    [Sheets.OpenRange, {}, "Cluster Total", "cluster_total"],
    [Sheets.YorNRange, SV.YoNValidation, "Loan / Loan Guarantee", "loan_guarantee"],
    [Sheets.OpenRange, {}, "If yes (Loan/Loan Guarantee, End of Audit Period Outstanding Loan Balance)", "outstanding_loan_balance"],
    [Sheets.YorNRange, {}, "If no (Direct Award), Name of Passthrough Entity", "is_direct_award"],
    [Sheets.OpenRange,
        {},  
        "If no (Direct Award), Identifying Number Assigned by the Pass-through Entity, if assigned", 
        "passthrough_identifying_number"],
    [Sheets.YorNRange, SV.YoNValidation, "Federal Award Passed Through to Subrecipients", "passed_through_to_recipients"],
    [Sheets.OpenRange, {}, "If yes (Passed Through), Amount Passed Through to Subrecipients", "amount_passed_to_subrecipients"],
    [Sheets.YorNRange, SV.YoNValidation, "Major Program (MP)", "is_major_program"],
    [Sheets.OpenRange, {}, "If yes (MP), Type of Audit Report", "type_of_audit_report"],
    [Sheets.OpenRange, SV.PositiveNumberValidation, "Number of Audit Findings", "number_of_audit_findings"],
];

local sheets = [
    {
        name: "Form",
        single_cells: single_cells,
        open_ranges: Fun.make_open_ranges(6, open_ranges_defns),
    },
];

local workbook = {
    filename: "federal-awards-expended-template-20230426.xlsx",
    sheets: sheets
};

{} + workbook