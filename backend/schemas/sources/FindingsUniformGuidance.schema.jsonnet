local Base = import 'Base.libsonnet';
local Requirement = import 'FindingsUniformGuidance.libsonnet';
local Additional = import 'FindingsUniformGuidance.validation.libsonnet';
local Func = import 'Functions.libsonnet';
local Types = Base.Types;
local Validations = Additional.Validations;

local Parts = {
  Program: Types.object {
    additionalProperties: false,
    properties: {
      program_name: Types.string,
      federal_agency_prefix: Base.Enum.ALNPrefixes,
      three_digit_extension: Base.Compound.ThreeDigitExtension,
      additional_award_identification: Types.string,
      compliance_requirement: Base.Compound.ComplianceRequirement,
    },
    required: ['program_name', 'federal_agency_prefix', 'three_digit_extension', 'compliance_requirement'],
    allOf: Base.Validation.AdditionalAwardIdentificationValidation,
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
    auditee_uei: Base.Compound.UEI,
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
