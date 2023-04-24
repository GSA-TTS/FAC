local Base = import 'Base.libsonnet';
local Requirement = import 'FindingsUniformGuidance.libsonnet';
local Func = import 'Functions.libsonnet';
local Additional = import 'FindingsUniformGuidance.validation.libsonnet';
local Types = Base.Types;
local Validations = Additional.Validations; 
local ComplianceRequirement = Requirement.ComplianceRequirement;

local Parts = {
  Program: Types.object {
    additionalProperties: false,
    properties: {
      name: Types.string,
      number: Base.Compound.ProgramNumber,
      compliance_requirement: ComplianceRequirement.ComplianceRequirement,
    },
    required: ['name', 'number', 'compliance_requirement'],
  },
  Findings:Types.object {
    additionalProperties: false,
    properties: {
      reference: Base.Compound.ReferenceNumber,
      is_valid: Base.Enum.YorN,
      repeat_prior_reference: Base.Enum.YorN,
      prior_references: Base.Compound.PriorReferences,      
    },     
    required: [
      'reference','repeat_prior_reference'
    ],
    oneOf: Validations.PriorReferences,
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
    required: ['program','findings','other_matters', 'material_weakness','significiant_deficiency','other_findings'],
    allOf: Validations.Combinations,
};

local FindingsUniformGuidance = Types.object {
  additionalProperties: false,
  properties: {
    auditee_ein: Func.compound_type([Types.string, Types.NULL]),
    findings_uniform_guidance_entries: Types.array {
      items: FindingsUniformGuidanceEntry,
    },
  },
  required: ['auditee_ein'],
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