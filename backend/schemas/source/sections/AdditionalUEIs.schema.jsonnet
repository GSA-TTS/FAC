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
