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
    // FIXME: 2023-08-07 MSHD: The 'Version' is currently used here as a placeholder, and it is not being enforced at the moment.
    // Once we establish a versioning pattern, we can update this and enforce it accordingly.
    version: Types.string {
      const: Sheets.WORKBOOKS_VERSION,
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
      compliance_requirement:{
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
