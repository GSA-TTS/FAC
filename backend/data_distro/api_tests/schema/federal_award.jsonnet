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
        finding_ref_numbers: Types.StringOrNull,
        amount: Types.integer,
        program_total: Types.integer,
        cluster_total: Types.integer,
        passthrough_amount: Types.integer,
        loan_balance: Types.StringOrNull,
        federal_program_name: Types.string,
        agency_name: Types.StringOrNull,
        award_identification: Types.string,
        agency_cfda: Types.string,
        cluster_name: Types.string,
        state_cluster_name: Types.StringOrNull,
        other_cluster_name: Types.string,
        type_requirement: Types.StringOrNull,
        type_report_major_program: Types.string,
        findings_count: Types.integer,
        audit_id: Types.integer,
        dbkey: Types.string,
        audit_year: Types.string,
        findings_page: Types.StringOrNull,
        questioned_costs: Types.StringOrNull,
        is_public: Types.boolean,
        cpa_ein: Types.integer,
        agency_prior_findings_list: Types.IntegerArray,
        general_id: Types.IntegerArray
    }
}
