local Base = import 'Base.libsonnet';
local Func = import 'Functions.libsonnet';
local Types = Base.Types;

local CorrectiveActionPlanEntry = {
    additionalProperties: false,
    properties: {
        reference_number: Types.string,
        planned_action: Types.string,
        contains_chart_or_table: Base.Enum.YorN
    },
};

local CorrectiveActionPlan = Types.object {
  additionalProperties: false,
  properties: {
    auditee_ein: Func.compound_type([Types.string, Types.NULL]),
    corrective_action_plan_entries: Types.array {
      items: CorrectiveActionPlanEntry,
    },
  },
  required: ['auditee_ein', 'corrective_action_plan_entries'],
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