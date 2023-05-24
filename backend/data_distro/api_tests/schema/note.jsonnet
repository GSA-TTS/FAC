local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer, // bigint?
    type_id: Types.integer,
    fac_id: Types.integer,
    report_id: Types.integer,
    version: Types.integer,
    sequence_number: Types.integer,
    note_index: Types.integer,
    content: Types.string, // Can maybe be null?
    title: Types.string,
    dbkey: Types.DBKEY,
    audit_year: Types.integer, // future REGEX type
    is_public: Types.boolean,
    general_id: [
        Types.integer
    ]
  }
}
