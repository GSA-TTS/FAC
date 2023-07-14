local Base = import '../base/Base.libsonnet';
local Func = import '../base/Functions.libsonnet';
local Types = Base.Types;

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
  required: ['auditee_uei', 'accounting_policies', 'is_minimis_rate_used'],
  title: 'NotesToSefa',
  version: 20230713,
};

local Root = Types.object {
  additionalProperties: false,
  properties: {
    NotesToSefa: NotesToSefa,
  },
  version: 20230713,
};

Base.SchemaBase + Root
