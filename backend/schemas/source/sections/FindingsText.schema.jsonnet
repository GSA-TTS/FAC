local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local FindingsTextEntry = {
  additionalProperties: false,
  properties: {
    reference_number: Base.Compound.ReferenceNumber,
    text_of_finding: Types.string,
    contains_chart_or_table: Base.Enum.YorN,
  },
  required: ['reference_number', 'text_of_finding', 'contains_chart_or_table'],
  title: 'FindingsTextEntry',
};

local FindingsText = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    findings_text_entries: Types.array {
      items: FindingsTextEntry,
    },
  },
  required: ['auditee_uei'],
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
