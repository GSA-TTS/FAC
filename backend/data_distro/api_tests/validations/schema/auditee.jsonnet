local Base = import '../../../../schemas/sources/Base.libsonnet';
local Types = Base.Types;

local REGEX_ZIPCODE = '^[0-9]{5}([0-9]{4})?$';
local REGEX_DBKEY = '[1-9][0-9]+';

local type_zipcode = Types.string {
  pattern: REGEX_ZIPCODE,
};


local type_string_or_null = {
  oneOf: [
    Types.NULL,
    Types.string,
  ],
};

local REGEX_UEI_ALPHA = 'A-H,J-N,P-Z,a-h,j-n,p-z';
local REGEX_UEI_LEADING = '[' + REGEX_UEI_ALPHA + ',1-9]';
local REGEX_UEI_BODY = '[' + REGEX_UEI_ALPHA + ',0-9]';

local type_uei = {
  type: 'array',
  allOf: [
    // Is a string
    {
      items: {
        type: 'string',
        minLength: 12,
        maxLength: 12,
      },
    },
    // Is alphanumeric, but no I or O
    {
      items: {
        pattern: '^' + REGEX_UEI_LEADING + REGEX_UEI_BODY + '+$',
      },
    },
    // Does not have 9 digits in a row
    {
      items: {
        pattern: '^(?!' + REGEX_UEI_LEADING + '+' + REGEX_UEI_BODY + '*?[0-9]{9})' + REGEX_UEI_BODY + '*$',
      },
    },
  ],
};

local auditee = Types.object {
  properties: {
    id: Types.integer,
    auditee_certify_name: type_string_or_null,
    auditee_certify_title: type_string_or_null,
    auditee_contact: type_string_or_null,
    auditee_email: Types.string,
    auditee_fax: type_string_or_null,
    auditee_name: Types.string,
    auditee_name_title: Types.string,
    auditee_phone: Types.integer,
    auditee_title: Types.string,
    auditee_street1: Types.string,
    auditee_street2: type_string_or_null,
    auditee_city: Types.string,
    auditee_state: Types.string,
    auditee_zip_code: Types.string {
      pattern: REGEX_ZIPCODE,
    },
    duns_list: {
      type: 'array',
      items: {
        type: 'integer',
      },
    },
    uei_list: type_uei,
    is_public: { type: 'boolean' },
    ein_subcode: type_string_or_null,
    ein_list: {
      type: 'array',
      items: {
        type: 'integer',
      },
    },
    general_id: {
      type: 'array',
      items: {
        type: 'integer',
      },
    },
    dbkey: {
      type: 'array',
      items: {
        type: 'string',
        pattern: REGEX_DBKEY,
      },
    },
  },

  required: [
    'id',
    'auditee_zip_code',
  ],
};

auditee
