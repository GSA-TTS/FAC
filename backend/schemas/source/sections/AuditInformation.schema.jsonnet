local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local AuditInformation = Types.object {
  additionalProperties: false,
  properties: {
    gaap_results: Types.array {
      items: Base.Enum.GAAPResults_GSAMigration,
    },
    sp_framework_basis: Types.array {
      items: Base.Enum.SP_Framework_Basis,
    },
    sp_framework_opinions: Types.array {
      items: Base.Enum.SP_Framework_Opinions,
    },
    dollar_threshold: Types.integer,
    is_sp_framework_required: {
      oneOf: [
        Types.boolean,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    is_going_concern_included: {
      oneOf: [
        Types.boolean,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    is_internal_control_deficiency_disclosed: {
      oneOf: [
        Types.boolean,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    is_internal_control_material_weakness_disclosed: {
      oneOf: [
        Types.boolean,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    is_material_noncompliance_disclosed: {
      oneOf: [
        Types.boolean,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    is_aicpa_audit_guide_included: {
      oneOf: [
        Types.boolean,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    is_low_risk_auditee: {
      oneOf: [
        Types.boolean,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    agencies: Types.array {
      items: Base.Compound.ALNPrefixesWithGsaMigration,
    },
  },
  required: [
    'dollar_threshold',
    'gaap_results',
    'is_going_concern_included',
    'is_internal_control_deficiency_disclosed',
    'is_internal_control_material_weakness_disclosed',
    'is_material_noncompliance_disclosed',
    'is_aicpa_audit_guide_included',
    'is_low_risk_auditee',
    'agencies',
  ],
  allOf: [
    {
      'if': {
        properties: {
          gaap_results: {
            contains: {
              const: 'not_gaap',
            },
          },
        },
      },
      'then': {
        required: ['is_sp_framework_required', 'sp_framework_basis', 'sp_framework_opinions'],
      },
    },
    {
      'if': {
        properties: {
          gaap_results: {
            not: {
              contains: {
                const: 'not_gaap',
              },
            },
          },
        },
      },
      'then': {
        not: {
          required: ['is_sp_framework_required'],
        },
      },
    },
    {
      'if': {
        properties: {
          gaap_results: {
            not: {
              contains: {
                const: 'not_gaap',
              },
            },
          },
        },
      },
      'then': {
        not: {
          required: ['sp_framework_basis'],
        },
      },
    },
    {
      'if': {
        properties: {
          gaap_results: {
            not: {
              contains: {
                const: 'not_gaap',
              },
            },
          },
        },
      },
      'then': {
        not: {
          required: ['sp_framework_opinions'],
        },
      },
    },
  ],
  title: 'AuditInformation',
};

// WARNING: If a comment is the last thing in a Jsonnet file, then the formatter will
// ALWAYS add a new line to the end of the file, meaning this file will change every
// time we run the formatter.
//
// To run local tests against an array of AuditInformation objects:
// create a new file that you would run the tests
// against that imports from this one, and wraps the AuditInformation object in an array.


local Root = Types.object {
  additionalProperties: false,
  properties: {
    AuditInformation: AuditInformation,
  },
  version: 20230719,
};

AuditInformation
