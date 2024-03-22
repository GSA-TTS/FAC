local ClusterNames = import 'ClusterNames.json';
local ComplianceRequirementTypes = import 'ComplianceRequirementTypes.json';
local FederalProgramNames = import 'FederalProgramNames.json';
local Func = import 'Functions.libsonnet';
local GAAP = import 'GAAP.libsonnet';
local States = import 'States.json';

local Const = {
  Y: 'Y',
  N: 'N',
  Y_N: 'Y&N',
  BOTH: "Both",
  NA: 'N/A',
  SCHEMA_VERSION: 'https://json-schema.org/draft/2019-09/schema#',
  empty_string: '',
  empty_array: [],
  empty_object: {},
  NULL: 'null',
  STATE_CLUSTER: 'STATE CLUSTER',
  OTHER_CLUSTER: 'OTHER CLUSTER NOT LISTED ABOVE',
  //A python version of `GSA_MIGRATION` exists in `settings.py`
  GSA_MIGRATION: 'GSA_MIGRATION',
};

local Types = {
  string: { type: 'string' },
  integer: { type: 'integer' },
  object: { type: 'object' },
  array: { type: 'array' },
  number: { type: 'number' },
  NULL: { type: Const.NULL },
  boolean: { type: 'boolean' },
};

// Support components for the Meta object.
// Use the leading _ for components we don't want
// to directly render.
local _Meta = {
  row: Types.integer {
    description: 'A row reference',
    minimum: 0,
  },
  column: Types.integer {
    description: 'A column reference',
    minimum: 0,
  },
  RC: Types.object {
    description: 'A row/column reference',
    properties: {
      row: _Meta.row,
      column: _Meta.column,
    },
    required: ['row', 'column'],
  },
};

local Meta = {
  error_location: {
    source_file: Types.object {
      description: 'Source file where an error occurred',
      properties: {
        RC: _Meta.RC,
        filename: Types.string,
        required: ['RC', 'filename'],
      },
    },
  },
};

# A python version of these regexes also exists in settings.py
local REGEX_ALN_PREFIX = '^([0-9]{2})$';
local REGEX_RD_EXTENSION = 'RD[0-9]?';
local REGEX_THREE_DIGIT_EXTENSION = '[0-9]{3}[A-Za-z]{0,1}';
local REGEX_U_EXTENSION = 'U[0-9]{2}';
local REGEX_NUMBER = '[0-9]+';

local type_aln_prefix = Types.string {
  allOf: [
    {
      minLength: 2,
      maxLength: 2,
    },
    {
      pattern: REGEX_ALN_PREFIX,
    },
  ],
};
local type_three_digit_extension = Types.string {
  pattern: '^('
           + REGEX_RD_EXTENSION
           + '|'
           + REGEX_THREE_DIGIT_EXTENSION
           + '|'
           + REGEX_U_EXTENSION
           + ')$',

};

local type_extension_rd_or_u = Types.string {
      pattern:'^(' + REGEX_RD_EXTENSION + '|' + REGEX_U_EXTENSION + ')$',
};

local Atoms = {

};

local Enum = {
  YorN: Types.string {
    // description: 'A yes or no answer',
    enum: [
      Const.Y,
      Const.N,
    ],
    //title: 'YorN'
  },
  YorNorGsaMigration: Types.string {
    enum: [
      Const.Y,
      Const.N,
      Const.GSA_MIGRATION,
    ],
  },
  YorNorBoth: Types.string {
    enum: [
      Const.Y,
      Const.N,
      Const.BOTH,
    ],
  },
  NA: Types.string {
    //description: 'A 'not applicable' answer',
    enum: [
      Const.NA,
    ],
    title: Const.NA,
  },
  EmptyString_Zero_Null: {
    description: 'Empty string, zero, or null expected.',
    enum: [
      Const.empty_string,
      0,
      Const.NULL,
    ],
    title: 'EmptyString_Zero_Null',
  },
  EmptyString_Null: {
    description: 'Empty string or null',
    enum: [
      Const.empty_string,
      Const.NULL,
    ],
    title: 'EmptyString_Null',
  },
  EmptyString_EmptyArray_Null: {
    description: 'Empty string, empty array, or null',
    enum: [
      Const.empty_string,
      Const.empty_array,
      Const.NULL,
    ],
    title: 'EmptyString_EmptyArray_Null',
  },
  AuditPeriod: Types.string {
    description: 'Period type of audit being submitted',
    enum: [
      'annual',
      'biennial',
      'other',
    ],
    title: 'AuditPeriod',
  },
  AuditType: Types.string {
    description: 'Type of audit being submitted',
    enum: [
      'program-specific',
      'single-audit',
    ],
    title: 'AuditType',
  },
  CountryType: Types.string {
    description: 'USA or International',
    enum: [
      'USA',
      'non-USA',
    ],
    title: 'CountryType',
  },
  MajorProgramAuditReportType: Types.string {
    description: 'Major program report types',
    enum: [
      'U',
      'Q',
      'A',
      'D',
    ],
    title: 'MajorProgramAuditReportType',
  },
  OrganizationType: Types.string {
    description: 'Org type',
    enum: [
      'state',
      'local',
      'tribal',
      'higher-ed',
      'non-profit',
      'unknown',
      'none',
    ],
    title: 'OrganizationType',
  },
  SubmissionStatus: Types.string {
    description: 'Submission status',
    enum: [
      'in_progress',
      'submitted',
      'received',
      'available',
    ],
    title: 'SubmissionStatus',
  },
  GAAPResults: Types.string {
    description: 'GAAP Results (Audit Information)',
    enum: std.map(function(pair) pair.key, GAAP.gaap_results),
  },
  SP_Framework_Basis: Types.string {
    description: 'SP Framework Basis (Audit Information)',
    enum: std.map(function(pair) pair.key, GAAP.sp_framework_basis),
  },
  SP_Framework_Opinions: Types.string {
    description: 'SP Framework Opinions (Audit Information)',
    enum: std.map(function(pair) pair.key, GAAP.sp_framework_opinions),
  },
  UnitedStatesStateAbbr: {
    description: 'US States 2-letter abbreviations',
    enum: States.UnitedStatesStateAbbr,
  },
};

local simple_phone_regex = '[1-9]{1}[0-9]{9}+';
local phone_regex = '^^(\\+0?1\\s)?\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}$';
local e164_regex = '^\\+[0-9]{1,3}[ ]*[0-9]{2,3}[ ]*[0-9]{2,3}[ ]*[0-9]{4}|^\\+[0-9]{1,3}[ ]*[0-9]{1,14}([ ]*[0-9]{1,13})?|^\\([0-9]{3}\\)[ ]*[0-9]{3}[ ]*[0-9]{4}?';
local email_regex = "^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$";


local REGEX_ZIPCODE = '^[0-9]{5}(?:[0-9]{4})?$';
local REGEX_DBKEY = '[1-9][0-9]+';
local REGEX_MONTHS_OTHER = '^0[0-9]|1[0-8]$';
local type_zipcode = Types.string {
  pattern: REGEX_ZIPCODE,
};

// UEIs are not case-sensitive, but we will upper-case all UEIs and store them
// as uppercase-only, so we're only dealing with uppercase letters in these patterns.
// This is not a *complete* UEI validator.
// However, it is a start of one.
// The UEI rules we know of are broken out so that all of the rules must apply.

// No I or O allowed.
local REGEX_UEI_ALPHA = 'A-HJ-NP-Z';
local REGEX_UEI_LEADING_CLOISTER = '[' + REGEX_UEI_ALPHA + '1-9]';
local REGEX_UEI_BODY_CLOISTER = '[' + REGEX_UEI_ALPHA + '0-9]';

local type_uei = Types.string {
  allOf: [
    // Is a string
    {
      minLength: 12,
      maxLength: 12,
    },
    {
      pattern: '^'
               + REGEX_UEI_LEADING_CLOISTER
               + REGEX_UEI_BODY_CLOISTER
               + '+$',
    },
    // Does not have 9 digits in a row
    {
      pattern: '^(?!'
               + REGEX_UEI_LEADING_CLOISTER
               + '+'
               + REGEX_UEI_BODY_CLOISTER
               + '*?[0-9]{9})'
               + REGEX_UEI_BODY_CLOISTER
               + '*$',
    },
    // Does not start with 9 digits in a row
    {
      pattern: '^(?![0-9]{9})',
    },
  ],
};

local Compound = {
  AwardReference: Types.string {
    title: 'AwardReference',
    description: 'Award Reference',
    pattern: '^AWARD-(?!0{4,5}$)[0-9]{4,5}$',
  },
  PriorReferences: Types.string {
    title: 'PriorReferences',
    description: 'Prior references',
    pattern: '^20[1-9][0-9]-[0-9]{3}(,\\s*20[1-9][0-9]-[0-9]{3})*$',
  },
  ReferenceNumber: Types.string {
    title: 'ReferenceNumber',
    description: 'Reference Number',
    pattern: '^20[1-9][0-9]-[0-9]{3}$',
  },
  ComplianceRequirement: {
    title: 'ComplianceRequirement',
    description: 'Compliance requirement type',
    pattern: '^A?B?C?E?F?G?H?I?J?L?M?N?P?$',
  },
  NonEmptyString: Types.string {
    minLength: 1,
  },
  EmployerIdentificationNumber: Types.string {
    pattern: '^[0-9]{9}$',
  },
  UniqueEntityIdentifier: {
    oneOf: [
      type_uei,
      Types.string {
        const: Const.GSA_MIGRATION,
      },
    ],
  },
  UnitedStatesPhone: Types.string {
    pattern: phone_regex,
  },
  Zip: type_zipcode,
  MonthsOther: Types.string {
    pattern: REGEX_MONTHS_OTHER,
  },
  EmptyString: Types.string {
    const: Const.empty_string,
  },
};


local SchemaBase = Types.object {
  '$schema': Const.SCHEMA_VERSION,
  additionalProperties: false,
  metamodel_version: '1.7.0',
  properties: Const.empty_object,
  title: 'UNNAMED',
  version: 0,
};

{
  Const: Const,
  Types: Types,
  Atoms: Atoms,
  Meta: Meta,
  Enum: Enum,
  Compound: Compound {
    FederalProgramNames: Types.string {
      description: 'All Federal program names',
      enum: FederalProgramNames.program_names,
    },
    AllALNNumbers: Types.string {
      description: 'All program numbers',
      enum: FederalProgramNames.all_alns,
    },
    ClusterNames: Types.string {
      description: 'All cluster names',
      enum: ClusterNames.cluster_names,
    },
    ClusterNamesNA: Types.string {
      description: 'All cluster names + N/A',
      enum: ClusterNames.cluster_names + [Const.NA],
    },
    ClusterNamesNAStateOther: Types.string {
      description: 'All cluster names',
      enum: ClusterNames.cluster_names + [Const.NA, Const.STATE_CLUSTER, Const.OTHER_CLUSTER],
    },
    ClusterNamesStateOther: Types.string {
      description: 'All cluster names',
      enum: ClusterNames.cluster_names + [Const.STATE_CLUSTER, Const.OTHER_CLUSTER],
    },
    ALNPrefixes: type_aln_prefix,
    ThreeDigitExtension: {
      oneOf: [
        type_three_digit_extension,
        Types.string {
          const: Const.GSA_MIGRATION,
        },
      ],
    },
    ComplianceRequirementTypes: {
      description: 'Compliance requirement types',
      enum: ComplianceRequirementTypes.requirement_types,
    },
    ExtensionRdOrU: type_extension_rd_or_u,
  },
  SchemaBase: SchemaBase,
}
