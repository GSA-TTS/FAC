local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer,
    charts_tables: Types.boolean,
    finding_ref_number: Types.string,
    sequence_number: Types.integer,
    text: Types.string,
    dbkey: Types.DBKEY,
    audit_year: Types.string,
    is_public: Types.boolean,
    general_id: Types.IntegerArray
  }
}
