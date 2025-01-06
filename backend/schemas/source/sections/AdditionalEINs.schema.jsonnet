local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';
local Types = Base.Types;

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.ADDITIONAL_EINS],
    },
    //Because we now pass the version to the SAC record,
    //we want to make sure we allow backwards compatibility
    version: Types.string {
      enum: ['1.0.0', '1.0.1', '1.0.2', '1.0.3', '1.0.4', '1.0.5', '1.1.0', '1.1.1', '1.1.2', Sheets.WORKBOOKS_VERSION],
    },
  },
  required: ['section_name'],
  title: 'Meta',
};

local AdditionalEinEntry = {
  additionalProperties: false,
  properties: {
    additional_ein: Base.Compound.EmployerIdentificationNumber,
  },
  required: ['additional_ein'],
  title: 'AdditionalEinEntry',
};

local AdditionalEINs = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    additional_eins_entries: Types.array {
      items: AdditionalEinEntry,
    },
  },
  required: ['auditee_uei'],
  title: 'AdditionalEINs',
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    AdditionalEINs: AdditionalEINs,
    Meta: Meta,
  },
};

Base.SchemaBase + Root
