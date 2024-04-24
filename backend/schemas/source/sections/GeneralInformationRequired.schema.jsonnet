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
  'ein',
  'ein_not_an_ssn_attestation',
  'is_usa_based',
  'met_spending_threshold',
  'multiple_eins_covered',
  'multiple_ueis_covered',
  'secondary_auditors_exist',
  'user_provided_organization_type',
  'auditee_zip',
  'auditor_country',
  'audit_period_covered',
];

GeneralInformation {
  required: RequiredField,
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
            not: {
              required: ['audit_period_other_months'],
            },
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
            not: {
              required: ['audit_period_other_months'],
            },
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
            required: ['audit_period_other_months'],
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
        allOf:[
          {
            not: {
              required: ['auditor_international_address'],
            },
          },
          {
            required: ['auditor_address_line_1', 'auditor_city', 'auditor_state','auditor_zip'],
          }
        ]
      },
    },
    // If auditor is NOT from the USA, international things should be filled in.
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
        allOf: [
          {
            not: {
              required: ['auditor_address_line_1', 'auditor_city', 'auditor_state','auditor_zip'],
            },
          },
          {
            required: ['auditor_international_address'],
          }
        ]
      },
    },
  ],
}
