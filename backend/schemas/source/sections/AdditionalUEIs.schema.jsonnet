local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';
local Types = Base.Types;

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.ADDITIONAL_UEIS],
    },
    //Because we now pass the version to the SAC record,
    //we want to make sure we allow backwards compatibility
    version: Types.string {
      enum: ['1.0.0', '1.0.1', '1.0.2', '1.0.3', '1.0.4', '1.0.5', '1.1.0', '1.1.1', '1.1.2', Sheets.WORKBOOKS_VERSION],
    },
  },
  required: ['section_name'],
  title: 'Meta',
  version: 20230807,
};

local AdditionalUeiEntry = {
  additionalProperties: false,
  properties: {
    additional_uei: Base.Compound.UniqueEntityIdentifier,
  },
  required: ['additional_uei'],
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
    Meta: Meta,
  },
  version: 20230621,
};

Base.SchemaBase + Root
