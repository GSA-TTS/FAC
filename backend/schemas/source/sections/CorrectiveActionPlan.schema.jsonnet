local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';
local Types = Base.Types;

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.CORRECTIVE_ACTION_PLAN],
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

local CorrectiveActionPlanEntry = {
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
    planned_action: Types.string,
    contains_chart_or_table: Base.Enum.YorNorGsaMigration,
  },
  required: ['reference_number', 'planned_action', 'contains_chart_or_table'],
  title: 'CorrectiveActionPlanEntry',
};

local CorrectiveActionPlan = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    corrective_action_plan_entries: Types.array {
      items: CorrectiveActionPlanEntry,
    },
  },
  required: ['auditee_uei'],
  title: 'CorrectiveActionPlan',
  version: 20230410,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    CorrectiveActionPlan: CorrectiveActionPlan,
    Meta: Meta,
  },
  version: 20230410,
};

Base.SchemaBase + Root
