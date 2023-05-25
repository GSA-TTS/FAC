local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer,
    modified_opinion: Types.boolean,
    other_non_compliance: Types.boolean,
    material_weakness: Types.boolean,
    significant_deficiency: Types.boolean,
    other_findings: Types.boolean,
    questioned_costs: Types.boolean,
    repeat_finding: Types.boolean,
    finding_ref_number: Types.string,
    prior_finding_ref_numbers: Types.StringOrNull,
    type_requirement: Types.StringOrNull,
    audit_id: Types.integer,
    audit_findings_id: Types.integer,
    audit_year: Types.string,
    dbkey: Types.DBKEY,
    is_public: Types.boolean,
    findings_text_id: Types.IntegerArray,
    general_id: Types.IntegerArray
}

}
