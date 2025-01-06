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

local FindingsTextEntry = {
  additionalProperties: false,
  properties: {
    reference_number: {
      oneOf: [
        Base.Compound.ReferenceNumber,
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
      ],
    },
    text_of_finding: Types.string,
    contains_chart_or_table: Base.Enum.YorNorGsaMigration,
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
