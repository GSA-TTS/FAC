local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local SecondaryAuditorsEntry = {
  additionalProperties: false,
  properties: {
    secondary_auditor_name: Types.string,
    secondary_auditor_ein: {
      '$ref': '#/$defs/EIN',
    },
    secondary_auditor_address_street: Types.string,
    secondary_auditor_address_city: Types.string,
    secondary_auditor_address_state: {
      '$ref': '#/$defs/State',
    },
    secondary_auditor_address_zipcode: {
      '$ref': '#/$defs/Zip',
    },
    secondary_auditor_contact_name: Types.string,
    secondary_auditor_contact_title: Types.string,
    secondary_auditor_contact_phone: {
      '$ref': '#/$defs/Phone',
    },
    secondary_auditor_contact_email: Types.string {
      format: 'email',
    },
  },
  required: ['secondary_auditor_name', 'secondary_auditor_ein', 'secondary_auditor_address_street', 'secondary_auditor_address_city', 'secondary_auditor_address_state', 'secondary_auditor_address_zipcode', 'secondary_auditor_contact_name', 'secondary_auditor_contact_title', 'secondary_auditor_contact_phone', 'secondary_auditor_contact_email'],
  title: 'SecondaryAuditorsEntry',
};

local SecondaryAuditors = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    secondary_auditors_entries: Types.array {
      items: SecondaryAuditorsEntry,
      minContains: 0,
    },
  },
  required: ['auditee_uei'],
  title: 'SecondaryAuditors',
  version: 20230714,
};

local Root = Types.object {
  additionalProperties: false,
  '$defs': {
    EIN: Func.join_types(Base.Compound.EmployerIdentificationNumber, [Types.NULL]),
    Phone: Base.Compound.UnitedStatesPhone,
    State: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
    Zip: Base.Compound.Zip,
  },
  properties: {
    SecondaryAuditors: SecondaryAuditors,
  },
  version: 20230714,
};

Base.SchemaBase + Root
