local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local AuditInformation = Types.object {
  additionalProperties: false,
  properties: {
    gaap_results: Types.array {
      items: Base.Enum.GAAPResults,
    },
    dollar_threshold: Types.integer,
    is_going_concern_included: Types.boolean,
    is_internal_control_deficiency_disclosed: Types.boolean,
    is_internal_control_material_weakness_disclosed: Types.boolean,
    is_material_noncompliance_disclosed: Types.boolean,
    is_aicpa_audit_guide_included: Types.boolean,
    is_low_risk_auditee: Types.boolean,
    // FIXME MCJ: This is a controlled field.
    // The validation needs to reflect that.
    agencies: Types.array {
      items: Base.Enum.ALNPrefixes,
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
