local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local AuditInformation = Types.object {
  additionalProperties: false,
  properties: {
    ggap_results: Types.array,
    is_going_concern_included: Types.boolean,
    is_internal_control_deficiency_disclosed: Types.boolean,
    is_internal_control_material_weakness_disclosed: Types.boolean,
    is_material_noncompliance_disclosed: Types.boolean,
    is_aicpa_audit_guide_included: Types.boolean,
    is_low_risk_auditee: Types.boolean,
    agencies: Types.array
  },
  required: ['ggap_results'],
  title: 'AuditInformation',
};


local Root = Types.object {
  additionalProperties: false,
  properties: {
    AuditInformation: AuditInformation,
  },
  version: 20230719,
};

Base.SchemaBase + Root
