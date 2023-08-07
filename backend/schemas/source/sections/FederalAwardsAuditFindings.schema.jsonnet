local Base = import '../base/Base.libsonnet';
local Additional = import 'FederalAwardsAuditFindings.validation.libsonnet';
local Types = Base.Types;
local Validations = Additional.Validations;

local Parts = {
  Program: Types.object {
    additionalProperties: false,
    properties: {
      award_reference: Base.Compound.AwardReference,
      compliance_requirement: Base.Compound.ComplianceRequirementTypes,
    },
    required: ['award_reference', 'compliance_requirement'],
  },
  Findings: Types.object {
    additionalProperties: false,
    properties: {
      reference_number: Base.Compound.ReferenceNumber,
      is_valid: Base.Enum.YorN,
      repeat_prior_reference: Base.Enum.YorN,
      prior_references: Base.Compound.PriorReferences,
    },
    required: [
      'reference_number',
      'repeat_prior_reference',
    ],
    oneOf: Validations.PriorReferences,
  },
};

local FindingsUniformGuidanceEntry = {
  additionalProperties: false,
  properties: {
    program: Parts.Program,
    findings: Parts.Findings,
    modified_opinion: Base.Enum.YorN,
    other_matters: Base.Enum.YorN,
    material_weakness: Base.Enum.YorN,
    significant_deficiency: Base.Enum.YorN,
    other_findings: Base.Enum.YorN,
    questioned_costs: Base.Enum.YorN,

  },
  required: ['program', 'findings', 'other_matters', 'material_weakness', 'significant_deficiency', 'other_findings'],
  allOf: Validations.Combinations,
};

local FindingsUniformGuidance = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    findings_uniform_guidance_entries: Types.array {
      items: FindingsUniformGuidanceEntry,
    },
  },
  required: ['auditee_uei'],
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
