local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

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
    audit_type: {
      oneOf: [
        Base.Enum.AuditType,
        Base.Compound.EmptyString,
      ]
    },
    audit_period_covered: {
      oneOf: [
        Base.Enum.AuditPeriod,
        Base.Compound.EmptyString,
      ]
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
      oneOf: [
        {
          format: 'email',
        },
        Base.Compound.EmptyString,
      ]
    },
    auditee_fiscal_period_end: Types.string {
      oneOf: [
        {
          format: 'date',
        },
        Base.Compound.EmptyString,
      ]
    },
    auditee_fiscal_period_start: Types.string {
      oneOf: [
        {
          format: 'date',
        },
        Base.Compound.EmptyString,
      ]
    },
    auditee_name: Func.compound_type([Types.string, Types.NULL]),
    auditee_phone: {
      oneOf: [
        Base.Compound.UnitedStatesPhone,
        Base.Compound.EmptyString,
      ]
    },
    auditee_state: {
      oneOf: [
        Base.Enum.UnitedStatesStateAbbr {
          title: 'State',
        },
        Base.Compound.EmptyString,
      ]
    },
    auditee_uei: {
      '$ref': '#/$defs/UEI',
    },
    auditee_zip: {
      anyOf: [
        Base.Compound.Zip,
        Base.Compound.EmptyString,
      ],
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
      oneOf: [
        Base.Compound.EmployerIdentificationNumber,
        Base.Compound.EmptyString,
      ],
    },
    auditor_ein_not_an_ssn_attestation: Func.compound_type([Types.boolean, Types.NULL]),
    auditor_email: Types.string {
      oneOf: [
        {
          format: 'email',
        },
        Base.Compound.EmptyString
      ]
    },
    
    auditor_firm_name: Types.string,
    auditor_phone: {
      oneOf: [
        Base.Compound.UnitedStatesPhone,
        Base.Compound.EmptyString,
      ]
    },
    auditor_state: {
      oneOf: [
        Base.Enum.UnitedStatesStateAbbr {
          title: 'State',
        },
        Base.Compound.EmptyString,
      ]
    },
    auditor_zip: {
      anyOf: [
        Base.Compound.Zip,
        Base.Compound.EmptyString,
      ],
    },
    ein: {
      oneOf: [
        Base.Compound.EmployerIdentificationNumber,
        Base.Compound.EmptyString,
      ],
    },
    ein_not_an_ssn_attestation: Func.compound_type([Types.boolean, Types.NULL]),
    is_usa_based: Types.boolean,
    met_spending_threshold: Types.boolean,
    multiple_eins_covered: Func.compound_type([Types.boolean, Types.NULL]),
    multiple_ueis_covered: Func.compound_type([Types.boolean, Types.NULL]),
    secondary_auditors_exist: Func.compound_type([Types.boolean, Types.NULL]),
    user_provided_organization_type: {
      oneOf: [
        Base.Enum.OrganizationType,
        Base.Compound.EmptyString,
      ],
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
          auditor_zip: {
            anyOf: [
              Base.Compound.Zip,
              Base.Compound.EmptyString,
            ],
          }
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
          auditor_zip: {
            anyOf: [
              Base.Compound.Zip,
              Base.Compound.EmptyString,
            ],
          }
        },
      },
    },
  ],
  required: [],
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
