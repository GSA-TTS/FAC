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

local Root = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Func.compound_type([Types.string, Types.NULL]),
    findings_text_entries: Types.array {
      items: FindingsTextEntry,
    },
  },
  required: ['auditee_uei', 'findings_text_entries'],
  title: 'FindingsText',
  version: 20230408,
};

local FederalAward = Types.object {
  additionalProperties: false,
  properties: {
    FindingsText: Root,
  },
  version: 20230408,
};

Base.SchemaBase + Root