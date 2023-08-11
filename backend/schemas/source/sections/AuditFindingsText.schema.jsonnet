local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';
local Types = Base.Types;

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.AUDIT_FINDINGS_TEXT],
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
    Meta: Meta,
  },
  version: 20230408,
};

Base.SchemaBase + Root
