local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local SecondaryAuditorsEntry = {
  additionalProperties: false,
  properties: {
    secondary_auditor_name: Types.string,
    secondary_auditor_ein: Func.join_types(Base.Compound.EmployerIdentificationNumber, [Types.NULL]),
    secondary_auditor_address_street: Types.string,
    secondary_auditor_address_city: Types.string,
    secondary_auditor_address_state: Base.Enum.UnitedStatesStateAbbr,
    secondary_auditor_address_zipcode: Base.Compound.Zip,
    secondary_auditor_contact_name: Types.string,
    secondary_auditor_contact_title: Types.string,
    secondary_auditor_contact_phone: Base.Compound.UnitedStatesPhone,
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
    },
  },
  required: ['auditee_uei'],
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
