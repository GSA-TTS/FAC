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
    // Audit information
    auditee_fiscal_period_start: Types.string {
      oneOf: [
        {
          format: 'date',
        },
        Base.Compound.EmptyString,
      ],
    },
    auditee_fiscal_period_end: Types.string {
      oneOf: [
        {
          format: 'date',
        },
        Base.Compound.EmptyString,
      ],
    },
    audit_type: {
      oneOf: [
        Base.Enum.AuditType,
        Base.Compound.EmptyString,
      ],
    },
    audit_period_covered: {
      oneOf: [
        Base.Enum.AuditPeriod,
        Base.Compound.EmptyString,
      ],
    },
    audit_period_other_months: Types.string {
      maxLength: 100,
    },

    // Auditee information
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    ein: {
      oneOf: [
        Base.Compound.EmployerIdentificationNumber,
        Base.Compound.EmptyString,
      ],
    },
    ein_not_an_ssn_attestation: Types.boolean,
    auditee_name: Types.string {
      maxLength: 100,
    },
    auditee_address_line_1: Types.string {
      maxLength: 100,
    },
    auditee_city: Types.string {
      maxLength: 100,
    },
    auditee_state: {
      oneOf: [
        Base.Enum.UnitedStatesStateAbbr {
          title: 'State',
        },
        Base.Compound.EmptyString,
      ],
    },
    auditee_zip: {
      anyOf: [
        Base.Compound.Zip,
        Base.Compound.EmptyString,
      ],
    },

    auditee_contact_name: Types.string {
      maxLength: 100,
    },
    auditee_contact_title: Types.string {
      maxLength: 100,
    },
    auditee_phone: {
      oneOf: [
        Base.Compound.UnitedStatesPhone,
        Base.Compound.EmptyString,
      ],
    },
    auditee_email: Types.string {
      oneOf: [
        Types.string {
          format: 'email',
          maxLength: 100,
        },
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
        Base.Compound.EmptyString,
      ],
    },

    // Auditor information
    auditor_ein: {
      oneOf: [
        Base.Compound.EmployerIdentificationNumber,
        Base.Compound.EmptyString,
      ],
    },
    auditor_ein_not_an_ssn_attestation: Types.boolean,
    auditor_firm_name: Types.string {
      maxLength: 100,
    },
    auditor_country: Base.Enum.CountryType,
    auditor_international_address: Types.string {
      maxLength: 100,
    },
    auditor_address_line_1: Types.string {
      maxLength: 100,
    },
    auditor_city: Types.string {
      maxLength: 100,
    },
    auditor_state: {
      anyOf: [
        Base.Enum.UnitedStatesStateAbbr {
          title: 'State',
        },
        Base.Compound.EmptyString,
      ],
    },
    auditor_zip: {
      anyOf: [
        Base.Compound.Zip,
        Base.Compound.EmptyString,
      ],
    },

    auditor_contact_name: Types.string {
      maxLength: 100,
    },
    auditor_contact_title: Types.string {
      maxLength: 100,
    },
    auditor_phone: {
      oneOf: [
        Base.Compound.UnitedStatesPhone,
        Base.Compound.EmptyString,
      ],
    },
    auditor_email: {
      oneOf: [
        Types.string {
          format: 'email',
          maxLength: 100,
        },
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
        Base.Compound.EmptyString,
      ],
    },
    // Others
    is_usa_based: Types.boolean,
    met_spending_threshold: Types.boolean,
    user_provided_organization_type: {
      oneOf: [
        Base.Enum.OrganizationType,
        Base.Compound.EmptyString,
      ],
    },
    multiple_eins_covered: Types.boolean,
    multiple_ueis_covered: Types.boolean,
    secondary_auditors_exist: Types.boolean,
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
          auditor_zip: {
            anyOf: [
              Base.Compound.Zip,
              Base.Compound.EmptyString,
            ],
          },
          auditor_state: {
            anyOf: [
              Base.Enum.UnitedStatesStateAbbr,
              Base.Compound.EmptyString,
            ],
          },
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
          auditor_state: Base.Compound.EmptyString,
        },
      },
    },
  ],
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
