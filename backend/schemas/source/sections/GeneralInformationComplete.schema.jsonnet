local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

/*
Checks all the fields to answer the question, "Is the form complete?"
Requires most fields, has consitional checks for conditional fields.
*/
{
  '$id': 'http://example.org/generalinformation',
  '$schema': 'http://json-schema.org/draft/2019-09/schema#',
  additionalProperties: false,
  metamodel_version: '1.7.0',
  properties: {
    // Audit information
    auditee_fiscal_period_start: {
      format: 'date',
    },
    auditee_fiscal_period_end: {
      format: 'date',
    },
    audit_type: Base.Enum.AuditType,
    audit_period_covered: Base.Enum.AuditPeriod,
    audit_period_other_months: Types.string,  // Conditional, no min/max length

    // Auditee information
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    ein: Base.Compound.EmployerIdentificationNumber,
    ein_not_an_ssn_attestation: Types.boolean,
    auditee_name: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditee_address_line_1: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditee_city: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditee_state: Base.Enum.UnitedStatesStateAbbr {
      title: 'State',
    },
    auditee_zip: Base.Compound.Zip,

    auditee_contact_name: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditee_contact_title: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditee_phone: Base.Compound.UnitedStatesPhone,
    auditee_email: {
      oneOf: [
        Types.string {
          format: 'email',
          maxLength: 100,
          minLength: 1,
        },
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },

    // Auditor information
    // Auditor address information is conditional based on country
    auditor_ein: Base.Compound.EmployerIdentificationNumber,
    auditor_ein_not_an_ssn_attestation: Types.boolean,
    auditor_firm_name: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditor_country: Base.Enum.CountryType,
    auditor_international_address: Types.string {
      maxLength: 100,
    },
    auditor_address_line_1: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditor_city: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditor_state: {
      oneOf: [
        Base.Enum.UnitedStatesStateAbbr,
        Base.Compound.EmptyString,
      ],
    },
    auditor_zip: {
      oneOf: [
        Base.Compound.Zip,
        Base.Compound.EmptyString,
      ],
    },

    auditor_contact_name: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditor_contact_title: Types.string {
      maxLength: 100,
      minLength: 1,
    },
    auditor_phone: Base.Compound.UnitedStatesPhone,
    auditor_email: {
      oneOf: [
        Types.string {
          format: 'email',
          maxLength: 100,
          minLength: 1,
        },
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    // Others
    is_usa_based: Types.boolean,
    met_spending_threshold: Types.boolean,
    user_provided_organization_type: Base.Enum.OrganizationType,
    multiple_eins_covered: Types.boolean,
    multiple_ueis_covered: Types.boolean,
    secondary_auditors_exist: Types.boolean,
  },
  allOf: [
    // If audit_period_covered is 'other', then audit_period_other_months should
    // have a value. Otherwise, it should have no value.
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
    // If auditor is from the USA, address info should be included.
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
    // If auditor is NOT from the USA, the zip should be empty.
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
    // The auditee EIN attestation should always be true.
    {
      properties: {
        ein_not_an_ssn_attestation: {
          const: true,
        },
      },
    },
    // The auditor EIN attestation should always be true.
    {
      properties: {
        auditor_ein_not_an_ssn_attestation: {
          const: true,
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
    'user_provided_organization_type',
  ],
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
