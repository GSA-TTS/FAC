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
