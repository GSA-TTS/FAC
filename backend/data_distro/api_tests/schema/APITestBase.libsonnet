local Base = import '../../../schemas/source/base/Base.libsonnet';
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

// No capital I or O, but lowercase is fine? FIXME check...
local REGEX_UEI_ALPHA = 'A-H,J-N,P-Z,a-z';
local REGEX_UEI_LEADING_CLOISTER = '[' + REGEX_UEI_ALPHA + ',1-9]';
local REGEX_UEI_BODY_CLOISTER = '[' + REGEX_UEI_ALPHA + ',0-9]';

// This may not be a *complete* UEI validator.
// However, it is a start of one. The UEI rules are broken
// out so that all of the rules must apply.
local type_uei = Types.string {
  allOf: [
    // Is a string
    {
      minLength: 12,
      maxLength: 12,
    },
    // Is alphanumeric, but no I or O
    {
      pattern: '^'
               + REGEX_UEI_LEADING_CLOISTER
               + REGEX_UEI_BODY_CLOISTER
               + '+$',
    },
    // Does not have 9 digits in a row
    {
      pattern: '^(?!'
               + REGEX_UEI_LEADING_CLOISTER
               + '+'
               + REGEX_UEI_BODY_CLOISTER
               + '*?[0-9]{9})'
               + REGEX_UEI_BODY_CLOISTER
               + '*$',
    },
  ],
};

local phone_regex = '[1-9]{1}[0-9]{9}+';
local e164_regex = '^\\+[0-9]{1,3}[ ]*[0-9]{2,3}[ ]*[0-9]{2,3}[ ]*[0-9]{4}|^\\+[0-9]{1,3}[ ]*[0-9]{1,14}([ ]*[0-9]{1,13})?|^\\([0-9]{3}\\)[ ]*[0-9]{3}[ ]*[0-9]{4}?';
local email_regex = '^[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\\.[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$';

// Extend the Base.Types object.
// Lets us transparently use the additional types in the
// API validations. Might want to move some of these back to the base.
// Also suggests we need to rethink/reorganize all of the validation/schema things.
Base {
  Types: Base.Types {
    boolean: { type: 'boolean' },
    BooleanOrNull: { type: ['boolean', Base.Const.NULL] },
    StringOrNull: type_string_or_null,
    UEI: type_uei,
    IntegerOrNull: { type: ['integer', Base.Const.NULL] },
    UEIArray: {
      type: 'array',
      items: type_uei,
    },
    // PhoneNumber: {
    //   type: 'integer',
    //   minimum: 1000000000,
    //   maximum: 9999999999,
    // },
    PhoneNumber: {
      type: 'string',
      pattern: e164_regex
    },
    Email: {
      type: 'string',
      pattern: email_regex
    },
    EmailOrNull: {
      type: ['string', Base.Const.NULL],
      oneOf: [
        {
          type: "string",
          pattern: email_regex
        },
        Types.NULL
      ],
    },
    ZIP: type_zipcode,
    DBKEY: Base.Types.string {
      pattern: REGEX_DBKEY,
    },
    IntegerArray: {
      type: 'array',
      items: Types.integer
    },
    IntegerArrayOrNull: {
      oneOf: [
        {
          type: 'array',
          items: Types.integer
        },
        {
          type: Base.Const.NULL
        }
      ]
    }
  },
}
