local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

/*
Checks all the fields to answer the question, "Is the form complete?"
Requires most fields, has consitional checks for conditional fields.
*/
{
  '$defs': {
    AuditPeriod: Base.Enum.AuditPeriod,
    EIN: Func.join_types(Base.Compound.EmployerIdentificationNumber, [Types.NULL]),
    Phone: Base.Compound.UnitedStatesPhone,
    State: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
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
    audit_period_covered: {
      '$ref': '#/$defs/AuditPeriod',
    },
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
    auditee_name: Func.compound_type([Types.string, Types.NULL]),
    auditee_phone: {
      '$ref': '#/$defs/Phone',
    },
    auditee_state: {
      '$ref': '#/$defs/State',
    },
    auditee_uei: {
      '$ref': '#/$defs/UEI',
    },
    auditee_zip: {
      '$ref': '#/$defs/Zip',
    },
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
    auditor_country: Base.Enum.CountryType,
    auditor_international_address: Types.string,
    auditor_ein: {
      '$ref': '#/$defs/EIN',
    },
    auditor_ein_not_an_ssn_attestation: Func.compound_type([Types.boolean, Types.NULL]),
    auditor_email: Types.string {
      format: 'email',
    },
    auditor_firm_name: Types.string,
    auditor_phone: {
      '$ref': '#/$defs/Phone',
    },
    auditor_state: {
      '$ref': '#/$defs/State',
    },
    auditor_zip: {
      anyOf: [
        Base.Compound.Zip,
        Base.Compound.EmptyString,
      ],
    },
    ein: {
      '$ref': '#/$defs/EIN',
    },
    ein_not_an_ssn_attestation: Func.compound_type([Types.boolean, Types.NULL]),
    is_usa_based: Types.boolean,
    met_spending_threshold: Types.boolean,
    multiple_eins_covered: Func.compound_type([Types.boolean, Types.NULL]),
    multiple_ueis_covered: Func.compound_type([Types.boolean, Types.NULL]),
    secondary_auditors_exist: Func.compound_type([Types.boolean, Types.NULL]),
    user_provided_organization_type: {
      '$ref': '#/$defs/UserProvidedOrganizationType',
    },
  },
  allOf: [
    {
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
    },
    {
      'if': {
        properties: {
          auditor_country: {
            const: 'USA',
          },
        },
      },
      'then': {
        properties: {
          auditor_zip: Base.Compound.Zip,
        },
      },
    },
    {
      'if': {
        properties: {
          auditor_country: {
            not: {
              const: 'USA',
            },
          },
        },
      },
      'then': {
        properties: {
          auditor_zip: Base.Compound.EmptyString,
        },
      },
    },
  ],
  required: [
    'audit_type',
    'auditee_address_line_1',
    'auditee_city',
    'auditee_contact_name',
    'auditee_contact_title',
    'auditee_email',
    'auditee_fiscal_period_end',
    'auditee_fiscal_period_start',
    'auditee_name',
    'auditee_phone',
    'auditee_state',
    'auditee_uei',
    'auditor_contact_name',
    'auditor_contact_title',
    'auditor_ein',
    'auditor_ein_not_an_ssn_attestation',
    'auditor_email',
    'auditor_firm_name',
    'auditor_phone',
    'auditor_state',
    'auditor_zip',
    'ein',
    'ein_not_an_ssn_attestation',
    'is_usa_based',
    'met_spending_threshold',
    'multiple_eins_covered',
    'multiple_ueis_covered',
    'secondary_auditors_exist',
    'user_provided_organization_type'
  ],
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
