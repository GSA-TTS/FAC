local Base = import 'APITestBase.libsonnet';
local Types = Base.Types;

Types.object {
  properties: {
    id: Types.integer,
    auditee_certify_name: Types.StringOrNull,
    auditee_certify_title: Types.StringOrNull,
    auditee_contact: Types.StringOrNull,
    auditee_email: Types.string,
    auditee_fax: Types.StringOrNull,
    auditee_name: Types.string,
    auditee_name_title: Types.string,
    auditee_phone: Types.PhoneNumber,
    auditee_title: Types.string,
    auditee_street1: Types.StringOrNull,
    auditee_street2: Types.StringOrNull,
    auditee_city: Types.string,
    auditee_state: Types.string,
    auditee_zip_code: Types.ZIP,
    duns_list: Types.IntegerArray,
    uei_list: {
      type: 'array',
      items: Types.UEI,
    },
    is_public: Types.boolean,
    ein_subcode: Types.StringOrNull,
    ein_list: Types.IntegerArray,
    general_id: Types.IntegerArray,
    dbkey: {
      type: 'array',
      items: Types.DBKEY,
    },
  },
  oneOf: [
    {
      properties: {
        auditee_street1: Types.string,
        auditee_street2: Types.NULL
      },
    },
    {
      properties: {
        auditee_street1: Types.NULL,
        auditee_street2: Types.string
      },
    },
    {
      properties: {
        auditee_street1: Types.string,
        auditee_street2: Types.string
      },
    },
  ],
  required: [
    'id',
    'auditee_zip_code',
  ],
}
