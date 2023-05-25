local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer,
    cpa_phone: Types.integer, // should this be a string?
    cpa_fax: Types.IntegerOrNull, // should this be a string?
    cpa_state: Types.string,
    cpa_city: Types.string,
    cpa_title: Types.string,
    cpa_street1: Types.string,
    cpa_street2: Types.StringOrNull,
    cpa_zip_code: Types.string,
    cpa_contact: Types.string,
    cpa_email: Types.string,
    cpa_firm_name: Types.string,
    cpa_ein: Types.IntegerOrNull,
    sequence_number: Types.IntegerOrNull,
    is_public: true,
    cpa_country: Types.StringOrNull,
    cpa_foreign: Types.StringOrNull,
    general_id: Types.IntegerArray,
    secondary_auditor_general_id: Types.IntegerArrayOrNull
  }
}
