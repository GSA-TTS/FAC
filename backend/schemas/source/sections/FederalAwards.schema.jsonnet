local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local Validations = {

  DirectAwardValidations: [
    {
      'if': {
        properties: {
          is_direct: {
            const: Base.Const.Y,
          },
        },
      },
      'then': {
        properties: {
          entities: Base.Enum.EmptyString_EmptyArray_Null,
        },
      },
    },
    {
      'if': {
        properties: {
          is_direct: {
            const: Base.Const.N,
          },
        },
      },
      'then': {
        required: [
          'entities',
        ],
      },
    },
  ],
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
          // 20230409 MCJ
          // FIXME: If the answer is Y, why can the balance be N/A?
          loan_balance_at_audit_period_end: {
            anyOf: [
              Types.integer {
                minimum: 1,
              },
              Base.Enum.NA,
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
        properties: {
          loan_balance_at_audit_period_end: Base.Enum.EmptyString_Zero_Null,
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
        properties: {
          subrecipient_amount: Types.integer,
        },
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
        properties: {
          subrecipient_amount: Base.Enum.EmptyString_Zero_Null,
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
        'if': {
          properties: {
            audit_report_type: {
              anyOf: [
                {
                  const: 'A',
                },
                {
                  const: 'Q',
                },
              ],
            },
          },
        },
        'then': {
          properties: {
            number_of_audit_findings: Types.integer {
              exclusiveMinimum: 0,
            },
          },
        },
      },
    },
    {
      // 20230409 MCJ FIXME: Should we require all fields always,
      // and make sure thet ype checking is correct in each conditional branch?
      // FIXME: Should we ALWAYS require a value in EVERY field, and disallow
      // the empty/null responses everywhere?
      'if': {
        properties: {
          is_major: {
            const: Base.Const.N,
          },
        },
      },
      'then': {
        properties: {
          audit_report_type: Base.Enum.EmptyString_Null,
        },
      },
    },
    Base.Validation.AdditionalAwardIdentificationValidation[0],
  ],
};

local Parts = {
  Cluster: Types.object {
    properties: {
      cluster_name: Base.Compound.ClusterNames,
      cluster_total: Types.number,
    },
    allOf: [
      {
        'if': {
          not: {
            properties: {
              cluster_name: {
                enum: [Base.Const.OTHER_CLUSTER, Base.Const.STATE_CLUSTER],
              },
            },
          },
        },
        'then': {
          allOf: [
            {
              properties: {
                other_cluster_name: Base.Enum.EmptyString_Null,
              },
            },
            {
              properties: {
                state_cluster_name: Base.Enum.EmptyString_Null,
              },
            },
          ],
        },
      },
      {
        'if': {
          properties: {
            cluster_name: {
              const: Base.Const.STATE_CLUSTER,
            },
          },
        },
        'then': {
          required: [
            'state_cluster_name',
          ],
          allOf: [
            {
              properties: {
                other_cluster_name: Base.Enum.EmptyString_Null,
              },
            },
            {
              properties: {
                state_cluster_name: Base.Compound.NonEmptyString,
              },
            },
          ],
        },
      },
      {
        'if': {
          properties: {
            cluster_name: {
              const: Base.Const.OTHER_CLUSTER,
            },
          },
        },
        'then': {
          required: [
            'other_cluster_name',
          ],
          allOf: [
            {
              properties: {
                other_cluster_name: Base.Compound.NonEmptyString,
              },
            },
            {
              properties: {
                state_cluster_name: Base.Enum.EmptyString_Null,
              },
            },
          ],
        },
      },
    ],
    required: ['cluster_name', 'cluster_total'],
  },
  PassThroughEntity: Types.object {
    additionalProperties: false,
    properties: {
      passthrough_name: Types.string,
      passthrough_identifying_number: {
        type: 'string',
        minLength: 1,
      },
    },
    required: ['passthrough_name', 'passthrough_identifying_number'],
  },
  DirectOrIndirectAward: Types.object {
    // 20230409 MCJ FIXME: I think this needs the amount...
    additionalProperties: false,
    description: 'If direct_award is N, the form must include a list of the pass-through entity by name and identifying number',
    properties: {
      is_direct: Base.Enum.YorN,
      entities: Types.array {
        items: Parts.PassThroughEntity,
      },
    },
    allOf: Validations.DirectAwardValidations,
  },
  LoanOrLoanGuarantee: Types.object {
    additionalProperties: false,
    description: 'A loan or loan guarantee and balance',
    properties: {
      is_guaranteed: Base.Enum.YorN,
      loan_balance_at_audit_period_end: Func.compound_type([Types.number, Types.string]),
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
      subrecipient_amount: Func.compound_type([Types.number, Types.string]),
    },
    allOf: Validations.SubrecipientValidations,
  },
  Program: Types.object {
    additionalProperties: false,
    properties: {
      federal_agency_prefix: Base.Enum.ALNPrefixes,
      three_digit_extension: Base.Compound.ThreeDigitExtension,
      additional_award_identification: Func.compound_type([Types.string, Types.NULL, Types.integer]),
      program_name: Types.string,
      amount_expended: Types.number,
      federal_program_total: Types.number,
      is_major: Base.Enum.YorN,
      audit_report_type: Func.compound_type([Base.Enum.MajorProgramAuditReportType, Types.NULL]),
      number_of_audit_findings: Types.integer,
    },
    required: ['program_name', 'federal_agency_prefix', 'three_digit_extension', 'is_major', 'number_of_audit_findings'],
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
    award_reference: Types.string,
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

local FederalAwards = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    federal_awards: Types.array {
      items: FederalAwardEntry,
    },
    total_amount_expended: Func.compound_type([Types.number {
      minimum: 0,
    }, Types.NULL]),
  },
  required: ['auditee_uei', 'total_amount_expended'],
  title: 'FederalAward',
  version: 20230408,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    FederalAwards: FederalAwards,
  },
  version: 20230408,
};

Base.SchemaBase + Root
