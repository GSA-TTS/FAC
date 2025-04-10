local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Sheets = import '../excel/libs/Sheets.libsonnet';
local Types = Base.Types;

local Meta = Types.object {
  additionalProperties: false,
  properties: {
    section_name: Types.string {
      enum: [Sheets.section_names.NOTES_TO_SEFA],
    },
    //Because we now pass the version to the SAC record,
    //we want to make sure we allow backwards compatibility
    version: Types.string {
      enum: [
        '1.0.0',
        '1.0.1',
        '1.0.2',
        '1.0.3',
        '1.0.4',
        '1.0.5',
        '1.1.0',
        '1.1.1',
        '1.1.2',
        '1.1.3',
        '1.1.4',
        '1.1.5',
        Sheets.WORKBOOKS_VERSION,
      ],
    },
  },
  required: ['section_name'],
  title: 'Meta',
  version: 20230807,
};

local NotesToSefaEntry = {
  additionalProperties: false,
  properties: {
    note_title: Types.string,
    note_content: Types.string,
    contains_chart_or_table: Base.Enum.YorNorGsaMigration,
    seq_number: Types.integer,
  },
  required: ['note_title', 'note_content', 'contains_chart_or_table'],
  title: 'NotesToSefaEntry',
};

local NotesToSefa = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    accounting_policies: Types.string,
    is_minimis_rate_used: {
      oneOf: [
        Types.string {
          const: Base.Const.GSA_MIGRATION,
        },
        Base.Enum.YorNorBoth,
      ],
    },
    rate_explained: Types.string,
    notes_to_sefa_entries: Types.array {
      items: NotesToSefaEntry,
    },
  },
  required: ['auditee_uei', 'accounting_policies', 'is_minimis_rate_used', 'rate_explained'],
  title: 'NotesToSefa',
  version: 20230713,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    NotesToSefa: NotesToSefa,
    Meta: Meta,
  },
  version: 20230713,
};

Base.SchemaBase + Root
