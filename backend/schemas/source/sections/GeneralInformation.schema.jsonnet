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
    audit_type: Base.Enum.AuditType,
    audit_period_covered: {
      '$ref': '#/$defs/AuditPeriod',
    },
    audit_period_months: Types.number{
      min: 0,
      max: 19, #  TODO What should the nax be?
    },
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
    auditor_country: Types.string {
      maxLength: 100,
    },
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
      '$ref': '#/$defs/Zip',
    },
    ein: {
      '$ref': '#/$defs/EIN',
    },
    ein_not_an_ssn_attestation: Func.compound_type([Types.boolean, Types.NULL]),
    is_usa_based: Types.boolean,
    met_spending_threshold: Types.boolean,
    multiple_eins_covered: Func.compound_type([Types.boolean, Types.NULL]),
    multiple_ueis_covered: Func.compound_type([Types.boolean, Types.NULL]),
    user_provided_organization_type: {
      '$ref': '#/$defs/UserProvidedOrganizationType',
    },
  },
  required: [],
  title: 'GeneralInformation',
  type: 'object',
  version: null,
}
