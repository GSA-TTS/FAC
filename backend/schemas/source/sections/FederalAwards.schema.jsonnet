local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';

local Types = Base.Types;

local Validations = {
  PassThroughEntity: Types.object {
    additionalProperties: false,
    properties: {
      passthrough_name: Types.string,
      passthrough_identifying_number: Types.string,
    },
    required: ['passthrough_name'],
  },
  LoanOrLoanGuaranteeValidations: [
    {
      'if': {
        properties: {
          is_guaranteed: {
            const: Base.Const.Y,
          },
        },
      },
      'then': {
        properties: {
          loan_balance_at_audit_period_end: {
            oneOf: [

              Types.string {
                pattern: '[0-9]+',
              }
              ,
              Types.string {
                const: Base.Const.NA,
              },
            ],
          },
        },
        required: ['loan_balance_at_audit_period_end'],
      },
    },
    {
      'if': {
        properties: {
          is_guaranteed: {
            const: Base.Const.N,
          },
        },
      },
      'then': {
        not: {
          required: ['loan_balance_at_audit_period_end'],
        },
      },
    },
  ],
  SubrecipientValidations: [
    {
      'if': {
        properties: {
          is_passed: {
            const: Base.Const.Y,
          },
        },
      },
      'then': {
        required: [
          'subrecipient_amount',
        ],
      },
    },
    {
      'if': {
        properties: {
          is_passed: {
            const: Base.Const.N,
          },
        },
      },
      'then': {
        not: {
          required: ['subrecipient_amount'],
        },
      },
    },
  ],
  ProgramValidations: [
    {
      properties: {
        number_of_audit_findings: Types.integer {
          minimum: 0,
        },
      },
    },
    {
      'if': {
        properties: {
          is_major: {
            const: Base.Const.Y,
          },
        },
      },
      'then': {
        required: ['audit_report_type'],
        // MCJ FIXME can we find in UG that this condition is true?
        // 'if': {
        //   properties: {
        //     audit_report_type: {
        //       anyOf: [
        //         {
        //           const: 'A',
        //         },
        //         {
        //           const: 'Q',
        //         },
        //       ],
        //     },
        //   },
        // },
        // 'then': {
        //   properties: {
        //     // If it is A or Q, then the number MUST be greater than 0.
        //     number_of_audit_findings: Types.integer {
        //       exclusiveMinimum: 0,
        //     },
        //   },
        // },
      },
    },
    {
      'if': {
        properties: {
          is_major: {
            const: Base.Const.N,
          },
        },
      },
      'then': {
        not: {
          required: ['audit_report_type'],
        },
      },
    },
    {
      'if': {
        properties: {
          three_digit_extension: Base.Compound.ExtensionRdOrU,
        },
      },
      'then': {
        properties: {
          additional_award_identification: Types.string {
            minLength: 1,
          },
        },
        required: ['additional_award_identification'],
      },
    },
  ],
};

local Parts = {
  Cluster: Types.object {
    properties: {
      cluster_name: Types.string,
      other_cluster_name: Types.string,
      state_cluster_name: Types.string,
      cluster_total: Types.number {
        minimum: 0,
      },
    },
    required: ['cluster_name', 'cluster_total'],
    allOf: [
      {
        'if': {
          properties: {
            cluster_name: Base.Compound.ClusterNamesNA,
          },
        },
        'then': {
          allOf: [
            {
              not: {
                required: ['other_cluster_name'],
              },
            },
            {
              not: {
                required: ['state_cluster_name'],
              },
            },
          ],

        },
      },
      {
        'if': {
          properties: {
            cluster_name: Types.string {
              const: Base.Const.OTHER_CLUSTER,
            },
          },
        },
        'then': {
          allOf: [
            {
              required: ['other_cluster_name'],
            },
            {
              not: {
                required: ['state_cluster_name'],
              },
            },

          ],

        },
      },
      {
        'if': {
          properties: {
            cluster_name: Types.string {
              const: Base.Const.STATE_CLUSTER,
            },
          },
        },
        'then': {
          allOf: [
            {
              required: ['state_cluster_name'],
            },
            {
              not: {
                required: ['other_cluster_name'],
              },
            },

          ],

        },
      },
    ],
  },

  DirectOrIndirectAward: Types.object {
    // 20230409 MCJ FIXME: I think this needs the amount...
    additionalProperties: false,
    description: 'If direct_award is N, the form must include a list of the pass-through entity by name and identifying number',
    properties: {
      is_direct: Base.Enum.YorN,
      entities: Types.array {
        items: Validations.PassThroughEntity,
      },
    },
    required: ['is_direct'],
    allOf: [
      {
        'if': {
          properties: {
            is_direct: {
              const: Base.Const.N,
            },
          },
        },
        'then': {
          required: ['entities'],
        },
      },
      {
        'if': {
          properties: {
            is_direct: {
              const: Base.Const.Y,
            },
          },
        },
        'then': {
          not: {
            required: ['entities'],
          },
        },
      },
    ],
  },
  LoanOrLoanGuarantee: Types.object {
    additionalProperties: false,
    description: 'A loan or loan guarantee and balance',
    properties: {
      is_guaranteed: Base.Enum.YorN,
      loan_balance_at_audit_period_end: Types.string,
    },
    required: [
      'is_guaranteed',
    ],
    allOf: Validations.LoanOrLoanGuaranteeValidations,
  },
  Subrecipients: Types.object {
    additionalProperties: false,
    properties: {
      is_passed: Base.Enum.YorN,
      subrecipient_amount: Types.number {
        minimum: 0,
      },
    },
    required: ['is_passed'],
    allOf: Validations.SubrecipientValidations,
  },
  Program: Types.object {
    additionalProperties: false,
    properties: {
      federal_agency_prefix: Base.Compound.ALNPrefixes,
      three_digit_extension: Base.Compound.ThreeDigitExtension,
      additional_award_identification: Types.string,
      program_name: Types.string,
      amount_expended: Types.number {
        minimum: 0,
      },
      federal_program_total: Types.number {
        minimum: 0,
      },
      is_major: Base.Enum.YorN,
      audit_report_type: Base.Enum.MajorProgramAuditReportType,
      number_of_audit_findings: Types.integer,
    },
    required: [
      'program_name',
      'federal_agency_prefix',
      'three_digit_extension',
      'is_major',
      'number_of_audit_findings',
      'federal_program_total',
      'amount_expended',
    ],
    allOf: Validations.ProgramValidations,
  },
};

local FederalAwardEntry = Types.object {
  additionalProperties: false,
  description: 'Award entry rows',
  properties: {
    cluster: Parts.Cluster,
    direct_or_indirect_award: Parts.DirectOrIndirectAward,
    loan_or_loan_guarantee: Parts.LoanOrLoanGuarantee,
    program: Parts.Program,
    subrecipients: Parts.Subrecipients,
    award_reference: Base.Compound.AwardReference,
  },
  required: [
    'cluster',
    'direct_or_indirect_award',
    'loan_or_loan_guarantee',
    'program',
    'subrecipients',
  ],
  title: 'FederalAwardEntry',
};

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.FEDERAL_AWARDS],
    },
    // FIXME: 2023-08-07 MSHD: The 'Version' is currently used here as a placeholder, and it is not being enforced at the moment.
    // Once we establish a versioning pattern, we can update this and enforce it accordingly.
    version: Types.string {
      const: Sheets.WORKBOOKS_VERSION,
    },
  },
  required: ['section_name'],
  title: 'Meta',
  version: 20230807,
};

local FederalAwards = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    federal_awards: Types.array {
      items: FederalAwardEntry,
    },
    total_amount_expended: Types.number {
      minimum: 0,
    },
  },
  required: ['auditee_uei', 'total_amount_expended'],
  title: 'FederalAward',
  version: 20230408,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    FederalAwards: FederalAwards,
    Meta: Meta,
  },
  version: 20230408,
};

Base.SchemaBase + Root
