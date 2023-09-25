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
    // FIXME: 2023-08-15 MSHD: The 'Version' is currently used here as a placeholder, and it is not being enforced at the moment.
    // Once we establish a versioning pattern, we can update this and enforce it accordingly.
    version: Types.string {
      const: Sheets.WORKBOOKS_VERSION,
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
