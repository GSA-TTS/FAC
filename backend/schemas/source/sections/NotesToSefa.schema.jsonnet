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

local NotesToSefaEntry = {
  additionalProperties: false,
  properties: {
    note_title: Types.string,
    note_content: Types.string,
    seq_number: Types.integer,
  },
  required: ['note_title', 'note_content'],
  title: 'NotesToSefaEntry',
};

local NotesToSefa = Types.object {
  additionalProperties: false,
  properties: {
    auditee_uei: Base.Compound.UniqueEntityIdentifier,
    accounting_policies: Types.string,
    is_minimis_rate_used: Base.Enum.YorNorBoth,
    rate_explained: Types.string,
    notes_to_sefa_entries: Types.array {
      items: NotesToSefaEntry,
    },
  },
  // 20230815 -- MCJ -- are any of these required?
  // 'accounting_policies',
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
