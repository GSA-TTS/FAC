local Base = import 'Base.libsonnet';
local Func = import 'Functions.libsonnet';
local Types = Base.Types;

local CorrectiveActionPlanEntry = {
  additionalProperties: false,
  properties: {
    reference_number: Base.Compound.ReferenceNumber,
    planned_action: Types.string,
    contains_chart_or_table: Base.Enum.YorN,
  },
  required: ['reference_number', 'planned_action', 'contains_chart_or_table'],
  title: 'CorrectiveActionPlanEntry',
};

local CorrectiveActionPlan = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UEI,
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
  },
  version: 20230410,
};

Base.SchemaBase + Root
