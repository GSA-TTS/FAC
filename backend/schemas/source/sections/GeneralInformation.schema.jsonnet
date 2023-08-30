local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

{
  '$defs': {
    AuditPeriod: Base.Enum.AuditPeriod,
    UEI: Base.Compound.UniqueEntityIdentifier,
    UserProvidedOrganizationType: Base.Enum.OrganizationType,
    Zip: Base.Compound.Zip,
  },
  '$id': 'http://example.org/generalinformation',
  '$schema': 'http://json-schema.org/draft/2019-09/schema#',
  additionalProperties: false,
  metamodel_version: '1.7.0',
  properties: {
    audit_type: Base.Enum.AuditType,
    audit_period_covered: Base.Enum.AuditPeriod,
    audit_period_other_months: Types.string,
    auditee_address_line_1: Types.string {
      maxLength: 100,
    },
    auditee_city: Types.string {
      maxLength: 100,
    },
    auditee_contact_name: Types.string {
      maxLength: 100,
    },
    auditee_contact_title: Types.string {
      maxLength: 100,
    },
    auditee_email: Types.string {
      format: 'email',
    },
    auditee_fiscal_period_end: Types.string {
      format: 'date',
    },
    auditee_fiscal_period_start: Types.string {
      format: 'date',
    },
    auditee_name: Types.string {
      maxLength: 100
    },
    auditee_phone: Base.Compound.UnitedStatesPhone,
    auditee_state: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    auditee_zip:  Base.Compound.Zip, //FIXME is this required
    auditor_address_line_1: Types.string {
      maxLength: 100,
    },
    auditor_city: Types.string {
      maxLength: 100,
    },
    auditor_contact_name: Types.string {
      maxLength: 100,
    },
    auditor_contact_title: Types.string {
      maxLength: 100,
    },
    auditor_country: Types.string {
      maxLength: 100,
    },
    auditor_ein: Base.Compound.EmployerIdentificationNumber,
    auditor_ein_not_an_ssn_attestation: Func.compound_type([Types.boolean, Types.NULL]),
    auditor_email: Types.string {
      format: 'email',
    },
    auditor_firm_name: Types.string,
    auditor_phone: Base.Compound.UnitedStatesPhone,
    auditor_state: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
    auditor_zip: {
      '$ref': '#/$defs/Zip',
    },
    ein: Base.Compound.EmployerIdentificationNumber,
    ein_not_an_ssn_attestation: Func.compound_type([Types.boolean, Types.NULL]),
    is_usa_based: Types.boolean,
    met_spending_threshold: Types.boolean,
    multiple_eins_covered: Types.boolean,
    multiple_ueis_covered: Types.boolean,
    secondary_auditors_exist: Func.compound_type([Types.boolean, Types.NULL]),
    user_provided_organization_type: {
      '$ref': '#/$defs/UserProvidedOrganizationType',
    },
  },
  required: [
    'auditee_contact_name',
    'auditee_email',
    'auditee_name',
    'auditee_phone',
    'auditee_contact_title',
    'auditee_address_line_1',
    'auditee_city',
    'auditee_state',
    'ein',
    'auditee_uei',



  ],
  anyOf: [
    {
      'if': {
        properties: {
          audit_period_covered: {
            const: 'annual',
          },
        },
      },
      'then': {
        audit_period_other_months: Base.Enum.EmptyString_Null,
      },
    },
    {
      'if': {
        properties: {
          audit_period_covered: {
            const: 'biennial',
          },
        },
      },
      'then': {
        audit_period_other_months: Base.Enum.EmptyString_Null,
      },
    },
    {
      'if': {
        properties: {
          audit_period_covered: {
            const: 'other',
          },
        },
      },
      'then': {
        audit_period_other_months: Base.Compound.MonthsOther,
      },
    },
  ],
  required: [],
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
