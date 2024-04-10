local single_cell = {
  type: 'single_cell',
  title: 'Example Cell',
  range_name: 'example_cell',
  title_cell: 'A1',
  range_cell: 'B1',
};

local meta_cell = {
  type: 'meta_cell',
  title: 'Example Meta Cell',
  title_cell: 'A1',
};

local open_range = {
  type: 'open_range',
  title: 'Example open range',
  range_name: 'Example open range',
  title_cell: 'A1',
  // Range start is redundant.
  // It should start below the title cell.
  // range_start: "B1"
};

local y_or_n_range = open_range {
  type: 'yorn_range',
  title: 'Example YorN range',
  range_name: 'Example YorN range',
};

// TODO: import from audits.fixtures.excel. Ref: https://github.com/GSA-TTS/FAC/issues/1673
local section_names = {
  CORRECTIVE_ACTION_PLAN: 'CorrectiveActionPlan',
  FEDERAL_AWARDS: 'FederalAwardsExpended',
  AUDIT_FINDINGS_TEXT: 'FindingsText',
  FEDERAL_AWARDS_AUDIT_FINDINGS: 'FindingsUniformGuidance',
  ADDITIONAL_UEIS: 'AdditionalUeis',
  ADDITIONAL_EINS: 'AdditionalEins',
  SECONDARY_AUDITORS: 'SecondaryAuditors',
  NOTES_TO_SEFA: 'NotesToSefa',
};

// All workbooks should get the same version number.
// When bumping, also add the new version to AUTHORIZED_VERSIONS in check_version_number.py
local WORKBOOKS_VERSION = '1.1.0';

{
  single_cell: single_cell,
  meta_cell: meta_cell,
  open_range: open_range,
  y_or_n_range: y_or_n_range,
  WORKBOOKS_VERSION: WORKBOOKS_VERSION,
  section_names: section_names
}
