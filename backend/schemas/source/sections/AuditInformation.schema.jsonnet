local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local AuditInformation = Types.object {
  //additionalProperties: false,
  properties: {
    gaap_results: Types.array {
      items: Base.Enum.GAAPResults,
    },
    sp_framework_basis: Types.array {
      items: Base.Enum.SP_Framework_Basis,
    },
    sp_framework_opinions: Types.array {
      items: Base.Enum.SP_Framework_Opinions,
    },
    dollar_threshold: Types.integer,
    is_going_concern_included: Types.boolean,
    is_internal_control_deficiency_disclosed: Types.boolean,
    is_internal_control_material_weakness_disclosed: Types.boolean,
    is_material_noncompliance_disclosed: Types.boolean,
    is_aicpa_audit_guide_included: Types.boolean,
    is_low_risk_auditee: Types.boolean,
    agencies: Types.array {
      items: Base.Compound.ALNPrefixes,
    },
  },
  //   is valid under each of {'properties':
  // {'is_sp_framework_required': {'type': 'boolean'}}}, {'properties':
  // {'is_sp_framework_required': {'const': ''}}}">
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
        properties: {
          is_sp_framework_required: Types.boolean,
        },
      },
    },
  ],
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
  title: 'AuditInformation',
};


local Root = Types.object {
  additionalProperties: false,
  properties: {
    AuditInformation: AuditInformation,
  },
  version: 20230719,
};

AuditInformation
