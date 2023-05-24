local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer,
    research_and_development: Types.BooleanOrNull,
    loans: Types.BooleanOrNull,
    arra: Types.BooleanOrNull,
    direct: Types.boolean,
    passthrough_award: Types.boolean,
    major_program: Types.boolean,
    finding_ref_numbers: Types.string,
    amount: Types.integer,
    program_total: Types.integer,
    cluster_total: Types.integer,
    passthrough_amount: Types.integer,
    loan_balance: Types.string,
    federal_program_name: Types.string,
    agency_name: Types.string,
    award_identification: Types.string,
    agency_cfda: Types.string,
    cluster_name: Types.string,
    state_cluster_name: Types.string,
    other_cluster_name: Types.string,
    type_requirement: Types.string,
    type_report_major_program: Types.string,
    findings_count: Types.integer,
    audit_id: Types.integer,
    dbkey: Types.string,
    audit_year: Types.string,
    findings_page: Types.string,
    questioned_costs: Types.string,
    is_public: Types.boolean,
    cpa_ein: Types.integer,
    agency_prior_findings_list: [
        Types.integer
    ],
    general_id: [
        Types.integer
    ]
}
