local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

// LOTS of optional fields here. 
Types.object {
  properties: {
    id: Types.integer,
    findings: Types.StringOrNull,
    revision_id: Types.IntegerOrNull, // this doesn't seem like it should be null, but there are some instances in the data
    federal_awards: Types.StringOrNull,
    general_info_explain: Types.StringOrNull,
    federal_awards_explain: Types.StringOrNull,
    notes_to_sefa_explain: Types.StringOrNull,
    audit_info_explain: Types.StringOrNull,
    findings_explain: Types.StringOrNull,
    findings_text_explain: Types.StringOrNull,
    cap_explain: Types.StringOrNull,
    other_explain: Types.StringOrNull,
    audit_info: Types.StringOrNull,
    notes_to_sefa: Types.StringOrNull,
    findings_text: Types.StringOrNull,
    cap: Types.StringOrNull,
    other: Types.StringOrNull,
    general_info: Types.StringOrNull,
    audit_year: Types.string,
    dbkey: Types.DBKEY,
    is_public: Types.boolean,
    // There are some missing general IDs, which implies some revision data
    // that isn't associated with any general report. This is probably not valid.
    general_id: Types.IntegerArray
  }
}
