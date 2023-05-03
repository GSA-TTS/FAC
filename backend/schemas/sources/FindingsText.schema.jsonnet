local Base = import 'Base.libsonnet';
local Func = import 'Functions.libsonnet';
local Types = Base.Types;

local FindingsTextEntry = {
    additionalProperties: false,
    properties: {
        reference_number: Base.Compound.ReferenceNumber,
        text_of_finding: Types.string,
        contains_chart_or_table: Base.Enum.YorN
    },
    required: ['reference_number', 'text_of_finding','contains_chart_or_table'],
    title: 'FindingsTextEntry',    
};

local FindingsText = Types.object {
  additionalProperties: false,
  properties: {
    auditee_ein: Func.compound_type([Types.string, Types.NULL]),
    findings_text_entries: Types.array {
      items: FindingsTextEntry,
    },
  },
  required: ['auditee_ein'],
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