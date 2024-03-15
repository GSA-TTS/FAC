local GeneralInformation = import 'GeneralInformation.schema.jsonnet';

local RequiredField = [
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

  //FIXME-MSHD: These fields were not enforced in GeneralInformationComplete.schema.jsonnet ???
  // 'auditee_zip',
  // 'auditor_address_line_1',
  // 'auditor_city',
  // 'auditor_country',
  // 'audit_period_covered',
];

GeneralInformation {
  required: RequiredField,
}
