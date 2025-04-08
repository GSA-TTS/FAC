local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';
local Types = Base.Types;

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.SECONDARY_AUDITORS],
    },
    //Because we now pass the version to the SAC record,
    //we want to make sure we allow backwards compatibility
    version: Types.string {
      enum: [
        '1.0.0',
        '1.0.1',
        '1.0.2',
        '1.0.3',
        '1.0.4',
        '1.0.5',
        '1.1.0',
        '1.1.1',
        '1.1.2',
        '1.1.3',
        '1.1.4',
        '1.1.5',
	'1.1.6',
        Sheets.WORKBOOKS_VERSION,
      ],
    },
  },
  required: ['section_name'],
  title: 'Meta',
  version: 20230807,
};

local SecondaryAuditorsEntry = {
  additionalProperties: false,
  properties: {
    secondary_auditor_name: Types.string,
    secondary_auditor_ein: Func.join_types(Base.Compound.EmployerIdentificationNumber, [Types.NULL]),
    secondary_auditor_address_street: Types.string,
    secondary_auditor_address_city: Types.string,
    secondary_auditor_address_state: {
      oneOf: [
        Base.Enum.UnitedStatesStateAbbr,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    secondary_auditor_address_zipcode: {
      oneOf: [
        Base.Compound.Zip,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
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
      minContains: 0,
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
    Meta: Meta,
  },
  version: 20230714,
};

Base.SchemaBase + Root
