local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local GeneralCharacterLimits = import '../base/character_limits/general.json';
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
    ein: {
      oneOf: [
        Base.Compound.EmployerIdentificationNumber,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    ein_not_an_ssn_attestation: Types.boolean,
    auditee_name: Types.string {
      minLength: GeneralCharacterLimits.auditee_name.min,
      maxLength: GeneralCharacterLimits.auditee_name.max,
    },
    auditee_address_line_1: Types.string {
      minLength: GeneralCharacterLimits.auditee_address_line_1.min,
      maxLength: GeneralCharacterLimits.auditee_address_line_1.max,
    },
    auditee_city: Types.string {
      minLength: GeneralCharacterLimits.auditee_city.min,
      maxLength: GeneralCharacterLimits.auditee_city.max,
    },
    auditee_state: Base.Enum.UnitedStatesStateAbbr,
    auditee_zip: {
      oneOf: [
        Base.Compound.Zip,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },

    auditee_contact_name: Types.string {
      minLength: GeneralCharacterLimits.auditee_contact_name.min,
      maxLength: GeneralCharacterLimits.auditee_contact_name.max,
    },
    auditee_contact_title: Types.string {
      minLength: GeneralCharacterLimits.auditee_contact_title.min,
      maxLength: GeneralCharacterLimits.auditee_contact_title.max,
    },
    auditee_phone: Base.Compound.UnitedStatesPhone,
    auditee_email: Types.string {
      oneOf: [
        Types.string {
          format: 'email',
          minLength: GeneralCharacterLimits.auditee_email.min,
          maxLength: GeneralCharacterLimits.auditee_email.max,
        },
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },

    // Auditor information
    auditor_ein: {
      oneOf: [
        Base.Compound.EmployerIdentificationNumber,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    auditor_ein_not_an_ssn_attestation: Types.boolean,
    auditor_firm_name: Types.string {
      minLength: GeneralCharacterLimits.auditor_firm_name.min,
      maxLength: GeneralCharacterLimits.auditor_firm_name.max,
    },
    auditor_country: Base.Enum.CountryType,
    auditor_international_address: Types.string {
      minLength: GeneralCharacterLimits.auditor_foreign_address.min,
      maxLength: GeneralCharacterLimits.auditor_foreign_address.max,
    },
    auditor_address_line_1: Types.string {
      minLength: GeneralCharacterLimits.auditor_address_line_1.min,
      maxLength: GeneralCharacterLimits.auditor_address_line_1.max,
    },
    auditor_city: Types.string {
      minLength: GeneralCharacterLimits.auditor_city.min,
      maxLength: GeneralCharacterLimits.auditor_city.max,
    },
    auditor_state: Base.Enum.UnitedStatesStateAbbr,
    auditor_zip: {
      oneOf: [
        Base.Compound.Zip,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },

    auditor_contact_name: Types.string {
      minLength: GeneralCharacterLimits.auditor_contact_name.min,
      maxLength: GeneralCharacterLimits.auditor_contact_name.max,
    },
    auditor_contact_title: Types.string {
      minLength: GeneralCharacterLimits.auditor_contact_title.min,
      maxLength: GeneralCharacterLimits.auditor_contact_title.max,
    },
    auditor_phone: Base.Compound.UnitedStatesPhone,
    auditor_email: {
      oneOf: [
        Types.string {
          format: 'email',
          minLength: GeneralCharacterLimits.auditor_email.min,
          maxLength: GeneralCharacterLimits.auditor_email.max,
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
