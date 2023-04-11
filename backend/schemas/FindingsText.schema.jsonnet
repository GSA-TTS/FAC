local Base = import 'Base.libsonnet';
local Func = import 'Functions.libsonnet';
local Types = Base.Types;

local FindingsTextEntry = {
    additionalProperties: false,
    properties: {
        reference_number: Types.string,
        text_of_finding: Types.string,
        contains_chart_or_table: Base.Enum.YorN
    },
};

local FindingsText = Types.object {
  additionalProperties: false,
  properties: {
    auditee_ein: Types.string,
    findings_text_entries: Types.array {
      items: FindingsTextEntry,
      minItems: 0
    },
  },
  required: ['auditee_ein', 'findings_text_entries'],
  title: 'FindingsText',
  version: 20230408,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    FindingsText: FindingsText,
  },
  version: 20230408,
};

Base.SchemaBase + Root