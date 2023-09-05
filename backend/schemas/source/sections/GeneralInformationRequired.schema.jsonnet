local GeneralInformation = import 'GeneralInformation.schema.jsonnet';

local RequiredField = [
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
  'auditee_zip',

  'auditor_phone',
  'auditor_state',
  'auditor_city',
  'auditor_contact_title',
  'auditor_address_line_1',
  'auditor_zip',
  'auditor_country',
  'auditor_contact_name',
  'auditor_email',
  'auditor_firm_name',
  // foreign address optional
  'auditor_ein',
  'auditee_fiscal_period_start',
  'auditee_fiscal_period_end',

  'audit_type',
  'user_provided_organization_type',

  // audit_period_other_months is optional
  'audit_period_covered',

  'multiple_eins_covered',
  'multiple_ueis_covered',
  'secondary_auditors_exist',
  'met_spending_threshold',
  'is_usa_based',
  'ein_not_an_ssn_attestation',
  'auditor_ein_not_an_ssn_attestation',


];

GeneralInformation {
  required: RequiredField,
}
