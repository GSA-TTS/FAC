local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer,
    passthrough_name: Types.string,
    passthrough_id: Types.StringOrNull, // This doesn't seem like something that should be optional, but there are nulls in the data 
    audit_id: Types.integer,
    audit_year: Types.string,
    dbkey: Types.DBKEY,
    is_public: Types.boolean,
    general_id: Types.IntegerArray
  }
}
