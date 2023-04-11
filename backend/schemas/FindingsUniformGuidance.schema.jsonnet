local Base = import 'Base.libsonnet';
local Func = import 'Functions.libsonnet';
local Types = Base.Types;


local Parts = {
   Program: Types.object {
    additionalProperties: false,
    properties: {
      name: Types.string,
      number: Types.string,
      compliance_requirement:  Types.array {
        description: 'Compliance requirement',
        contains: {
          enum: [
            'A',
            'B',
            'C',
            'E',
            'F',
            'G',
            'H',
            'I',
            'J',
            'L',
            'M',
            'N',
            'P'
          ],
        },
      },
    },
    required: [
      'compliance_requirement'
    ],
  },
  Findings:Types.object { 
    reference: Types.string,
    is_valid: Base.Enum.YorN,
    repeat_prior_reference: Base.Enum.YorN,
    prior_references: Types.array {
      items: Types.string,
    },
    required: [
      'reference','repeat_prior_reference','prior_references'
    ],
  }, 
};

local FindingsUniformGuidanceEntry = {
    additionalProperties: false,
    properties: {
        program: Parts.Program,
        findings:Parts.Findings,
        modified_opinion: Base.Enum.YorN,
        other_matters: Base.Enum.YorN,
        material_weakness: Base.Enum.YorN,
        significiant_deficiency: Base.Enum.YorN,
        other_findings: Base.Enum.YorN,
        questioned_costs: Base.Enum.YorN,

    },
};

local FindingsUniformGuidance = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Func.compound_type([Types.string, Types.NULL]),
    findings_uniform_guidance_entries: Types.array {
      items: FindingsUniformGuidanceEntry,
    },
  },
  required: ['auditee_uei', 'findings_uniform_guidance_entries'],
  title: 'FindingsUniformGuidance',
  version: 20230410,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    FindingsUniformGuidance: FindingsUniformGuidance,
  },
  version: 20230410,
};

Base.SchemaBase + Root