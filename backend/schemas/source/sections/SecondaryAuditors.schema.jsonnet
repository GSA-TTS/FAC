local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local SecondaryAuditorsEntry = {
  '$defs': {
    EIN: Func.join_types(Base.Compound.EmployerIdentificationNumber, [Types.NULL]),
    Phone: Base.Compound.UnitedStatesPhone,
    State: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
    Zip: Base.Compound.Zip,
  },
  additionalProperties: false,
  properties: {
    secondary_auditor_name: Types.string,
    secondary_auditor_ein: {
      '$ref': '#/$defs/EIN',
    },
    secondary_auditor_address: Types.string,
    secondary_auditor_city: Types.string,
    secondary_auditor_state: {
      '$ref': '#/$defs/State',
    },
    secondary_auditor_zip: {
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
  required: ['secondary_auditor_name', 'secondary_auditor_ein', 'secondary_auditor_address', 'secondary_auditor_city', 'secondary_auditor_state', 'secondary_auditor_zip', 'secondary_auditor_contact_name', 'secondary_auditor_contact_title', 'secondary_auditor_contact_phone', 'secondary_auditor_contact_email'],
  title: 'SecondaryAuditorsEntry',
};

local SecondaryAuditors = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    secondary_auditors_entries: Types.array {
      items: SecondaryAuditorsEntry,
    },
  },
  required: ['auditee_uei', 'secondary_auditors_entries'],
  title: 'SecondaryAuditors',
  version: 20230714,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    SecondaryAuditors: SecondaryAuditors,
  },
  version: 20230714,
};

Base.SchemaBase + Root
