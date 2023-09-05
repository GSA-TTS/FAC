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
    auditee_name: Types.string {
      maxLength: 100,
    },
    auditee_phone: Base.Compound.UnitedStatesPhone,
    auditee_state: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    auditee_zip: Base.Compound.Zip,
    ein: Base.Compound.EmployerIdentificationNumber,


    auditor_phone: Base.Compound.UnitedStatesPhone,
    auditor_state: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
    auditor_city: Types.string {
      maxLength: 100,
    },
    auditor_contact_title: Types.string {
      maxLength: 100,
    },
    auditor_address_line_1: Types.string {
      maxLength: 100,
    },
    auditor_zip: Base.Compound.Zip,
    auditor_country: Types.string {
      maxLength: 100,
    },
    auditor_contact_name: Types.string {
      maxLength: 100,
    },
    auditor_email: Types.string {
      format: 'email',
    },
    auditor_firm_name: Types.string,
    auditor_foreign_address: Types.string,
    auditor_ein: Base.Compound.EmployerIdentificationNumber,

    auditee_fiscal_period_start: Types.string {
      format: 'date',
    },
    auditee_fiscal_period_end: Types.string {
      format: 'date',
    },
    audit_type: Base.Enum.AuditType,
    user_provided_organization_type: Base.Enum.OrganizationType,
    audit_period_other_months: Types.string,
    audit_period_covered: Base.Enum.AuditPeriod,

    auditor_ein_not_an_ssn_attestation: Types.boolean,
    ein_not_an_ssn_attestation: Types.boolean,

    is_usa_based: Types.boolean,
    met_spending_threshold: Types.boolean,

    multiple_eins_covered: Types.boolean,
    multiple_ueis_covered: Types.boolean,
    secondary_auditors_exist: Types.boolean,

  },
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
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
