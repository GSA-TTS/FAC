local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local Validations = {
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
  PassThroughEntityEmpty: Types.object {
    additionalProperties: false,
    properties: {
      passthrough_name: Base.Enum.EmptyString_Null,
      passthrough_identifying_number: Base.Enum.EmptyString_Null,
    },
    required: ['passthrough_name', 'passthrough_identifying_number'],
  },
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
          entities: {
            anyOf: [
              Types.array {
                items: Validations.PassThroughEntityEmpty,
              },
              Base.Enum.EmptyString_EmptyArray_Null,
            ],
          },
        },
        // 20230627 MCJ Not required to be present if "Y"
        // required: [
        //   'entities',
        // ],
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
        properties: {
          entities: Types.array {
            items: Validations.PassThroughEntity,
          },
        },
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
        required: ['audit_report_type'],
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
            // If it is A or Q, then the number MUST be greater than 0.
            number_of_audit_findings: Types.integer {
              exclusiveMinimum: 0,
            },
          },
        },
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
        properties: {
          audit_report_type: Base.Enum.EmptyString_Null,
        },
      },
    },
    Base.Validation.AdditionalAwardIdentificationValidation[0],
  ],
};

local Parts = {
  // FIXME
  // cluster_name should always be present.
  // At the least, it should always be N/A.
  Cluster: Types.object {
    properties: {
      // Cluster name must always be present, and it must EITHER be:
      //  - A valid cluster name from the enumeration
      //  - N/A
      //  - STATE CLUSTER, or
      //  - the designation for other cluster name
      cluster_name: Base.Compound.ClusterNamesNAStateOther,
      cluster_total: Types.number {
        minimum: 0,
      },
    },
    allOf: [
      {
        'if': {
          properties: {
            cluster_total: Types.number {
              const: 0,
            },
          },
        },
        'then': {
          allOf: [
            {
              properties: {
                cluster_name: Base.Enum.NA,
              },
            },  
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
        // If I have a cluster_total greater than zero, then I
        // must have a valid cluster name. It cannot be N/A if the
        // cluster total is greater than zero.
        'if': {
          properties: {
            cluster_total: Types.number {
              exclusiveMinimum: 0,
            },
          },
        },
        'then': {
          allOf: [
            {
              properties: {
                cluster_name: Base.Compound.ClusterNamesStateOther,
              },
            },
            // IF we have OTHER_CLUSTER, THEN...
            //   - other_cluster_name is required
            //   - other_cluster_name must not be empty
            //   - state_cluster_name must be empty
            {
              'if': {
                properties: {
                  cluster_name: {
                    const: Base.Const.OTHER_CLUSTER,
                  },
                },
              },
              'then': {
                required: ['other_cluster_name'],
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
            // IF we have STATE_CLUSTER, THEN...
            //   - state_cluster_name is required
            //   - state_cluster_name must not be empty
            //   - other_cluster_name must be empty
            {
              'if': {
                properties: {
                  cluster_name: {
                    const: Base.Const.STATE_CLUSTER,
                  },
                },
              },
              'then': {
                required: ['state_cluster_name'],
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
          ],
        },
      },
    ],
    // Handle all requireds conditionally?
    required: ['cluster_name', 'cluster_total'],
  },

  DirectOrIndirectAward: Types.object {
    // 20230409 MCJ FIXME: I think this needs the amount...
    additionalProperties: false,
    description: 'If direct_award is N, the form must include a list of the pass-through entity by name and identifying number',
    properties: {
      is_direct: Base.Enum.YorN,
      entities: Types.array,
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
      federal_agency_prefix: Base.Compound.ALNPrefixes,
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
