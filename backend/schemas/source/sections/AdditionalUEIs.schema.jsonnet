local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

local AdditionalUeiEntry = {
  additionalProperties: false,
  properties: {
    seq_number: Types.integer,
    additional_uei: Base.Compound.UniqueEntityIdentifier,
  },
  required: ['seq_number', 'additional_uei'],
  title: 'AdditionalUeiEntry',
};

local AdditionalUEIs = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    additional_ueis_entries: Types.array {
      items: AdditionalUeiEntry,
    },
  },
  required: ['auditee_uei'],
  title: 'AdditionalUEIs',
  version: 20230621,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    AdditionalUEIs: AdditionalUEIs,
  },
  version: 20230621,
};

Base.SchemaBase + Root
