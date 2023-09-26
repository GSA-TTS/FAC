local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

/*
Typechecks fields, but allows for empty data as well. Contains conditional Checks.
*/
{
  '$id': 'http://example.org/generalinformation',
  '$schema': Base.Const.SCHEMA_VERSION,
  additionalProperties: false,
  metamodel_version: '1.7.0',
  properties: {
    tribal_authorization_certifying_official_title: Types.string,
    is_tribal_information_authorized_to_be_public: Types.boolean,
    tribal_authorization_certifying_official_name: Types.string,
  },
  required: [
    'tribal_authorization_certifying_official_title',
    'is_tribal_information_authorized_to_be_public',
    'tribal_authorization_certifying_official_name'
  ],
  title: 'TribalAccess',
  type: 'object',
  version: null,
}
