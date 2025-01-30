local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';
local Additional = import 'FederalAwardsAuditFindings.validation.libsonnet';
local Types = Base.Types;
local Validations = Additional.Validations;
local Func = import '../base/Functions.libsonnet';

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.FEDERAL_AWARDS_AUDIT_FINDINGS],
    },
    //Because we now pass the version to the SAC record,
    //we want to make sure we allow backwards compatibility
    version: Types.string {
      enum: ['1.0.0', '1.0.1', '1.0.2', '1.0.3', '1.0.4', '1.0.5', '1.1.0', '1.1.1', '1.1.2', '1.1.3', Sheets.WORKBOOKS_VERSION],
    },
  },
  required: ['section_name'],
  title: 'Meta',
  version: 20230807,
};

local Parts = {
  Program: Types.object {
    additionalProperties: false,
    properties: {
      award_reference: Base.Compound.AwardReference,
      compliance_requirement: {
        oneOf: [
          Base.Compound.ComplianceRequirementTypes,
          Types.string {
            const: Base.Const.GSA_MIGRATION,
          },
        ],
      },
    },
    required: ['award_reference', 'compliance_requirement'],
  },
  Findings: Types.object {
    additionalProperties: false,
    properties: {
      reference_number: {
        oneOf: [
          Base.Compound.ReferenceNumber,
          Types.string {
            const: Base.Const.GSA_MIGRATION,
          },
        ],
      },
      is_valid: Base.Enum.YorNorGsaMigration,
      repeat_prior_reference: Base.Enum.YorNorGsaMigration,
      prior_references: Types.string,
    },
    required: [
      'reference_number',
      'prior_references',
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
    modified_opinion: Base.Enum.YorNorGsaMigration,
    other_matters: Base.Enum.YorNorGsaMigration,
    material_weakness: Base.Enum.YorNorGsaMigration,
    significant_deficiency: Base.Enum.YorNorGsaMigration,
    other_findings: Base.Enum.YorNorGsaMigration,
    questioned_costs: Base.Enum.YorNorGsaMigration,

  },
  required: [
    'program',
    'findings',
    'other_matters',
    'material_weakness',
    'modified_opinion',
    'significant_deficiency',
    'other_findings',
    'questioned_costs',
  ],
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
    Meta: Meta,
  },
  version: 20230410,
};

Base.SchemaBase + Root
