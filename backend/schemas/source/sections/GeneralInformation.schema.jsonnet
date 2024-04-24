local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

/*
Typechecks fields, but allows for empty data as well. Contains conditional checks.
*/
{
  '$id': 'http://example.org/generalinformation',
  '$schema': Base.Const.SCHEMA_VERSION,
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
    audit_period_other_months: Base.Compound.MonthsOther,

    // Auditee information
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    ein: Base.Compound.EmployerIdentificationNumber,
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
    auditee_state: Base.Enum.UnitedStatesStateAbbr,
    auditee_zip: Base.Compound.Zip,

    auditee_contact_name: Types.string {
      maxLength: 100,
    },
    auditee_contact_title: Types.string {
      maxLength: 100,
    },
    auditee_phone: Base.Compound.UnitedStatesPhone,
    auditee_email: Types.string {
      oneOf: [
        Types.string {
          format: 'email',
          maxLength: 100,
        },
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },

    // Auditor information
    auditor_ein: Base.Compound.EmployerIdentificationNumber,
    auditor_ein_not_an_ssn_attestation: Types.boolean,
    auditor_firm_name: Types.string {
      maxLength: 100,
    },
    auditor_country: Base.Enum.CountryType,
    auditor_international_address: Types.string {
      minLength: 1,
      maxLength: 500,
    },
    auditor_address_line_1: Types.string {
      minLength: 1,
      maxLength: 100,
    },
    auditor_city: Types.string {
      minLength: 1,
      maxLength: 100,
    },
    auditor_state: Base.Enum.UnitedStatesStateAbbr,
    auditor_zip: Base.Compound.Zip,

    auditor_contact_name: Types.string {
      maxLength: 100,
    },
    auditor_contact_title: Types.string {
      maxLength: 100,
    },
    auditor_phone: Base.Compound.UnitedStatesPhone,
    auditor_email: {
      oneOf: [
        Types.string {
          format: 'email',
          maxLength: 100,
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
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
