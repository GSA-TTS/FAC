local Const = {
  Y: 'Y',
  N: 'N',
  NA: 'N/A',
  SCHEMA_VERSION: 'https://json-schema.org/draft/2019-09/schema#',
  empty_string: '',
  empty_array: [],
  empty_object: {},
  NULL: 'null',
  STATE_CLUSTER: 'STATE CLUSTER',
  OTHER_CLUSTER: 'OTHER CLUSTER NOT LISTED ABOVE',
};

local Types = {
  string: { type: 'string' },
  integer: { type: 'integer' },
  object: { type: 'object' },
  array: { type: 'array' },
  number: { type: 'number' },
  NULL: { type: Const.NULL },
  boolean: { type: 'boolean' },
  boolean_or_null: { type: ['boolean', 'null'] },
  string_or_null: { type: ['string', 'null'] },
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
    title: 'EmptyString_Null',
  },
  UnitedStatesStateAbbr: Types.string {
     'enum': [
        'AL',
        'AK',
        'AZ',
        'AR',
        'CA',
        'CO',
        'CT',
        'DE',
        'FL',
        'GA',
        'HI',
        'ID',
        'IL',
        'IN',
        'IA',
        'KS',
        'KY',
        'LA',
        'ME',
        'MD',
        'MA',
        'MI',
        'MN',
        'MS',
        'MO',
        'MT',
        'NE',
        'NV',
        'NH',
        'NJ',
        'NM',
        'NY',
        'NC',
        'ND',
        'OH',
        'OK',
        'OR',
        'PA',
        'RI',
        'SC',
        'SD',
        'TN',
        'TX',
        'UT',
        'VT',
        'VA',
        'WA',
        'WV',
        'WI',
        'WY'
     ],
  },
  AuditPeriod: Types.string {
     description: 'Period type of audit being submitted',
     enum: [
        'annual',
        'biennial',
        'other'
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
};

local Compound = {
  ProgramNumber: Types.string {
    title: 'ProgramNumber',
    description: 'Program number',
    pattern: '^[1-9]{1}[0-9]{1}\\.([0-9]{3}[a-zA-Z]{0,1}|U[0-9]{2}|RD)$',
  },
  ComplianceRequirement: Types.string {
    title: 'ComplianceRequirement',
    description: 'Compliance requirement type',
    pattern: '^(([ABCEFGHIJLMNP])(?!.*\\2))+$',
  },
  PriorReferences: Types.string {
    title: 'PriorReferences',
    description: 'Prior references',
    pattern: '^(20[2-9]{1}[0-9]{1}-[0-9]{3},?)+$',
  },
  ReferenceNumber: Types.string {
    title: 'ReferenceNumber',
    description: 'Reference Number',
    pattern: '^20[2-9]{1}[0-9]{1}-[0-9]{3}$',
  },  
  ClusterName: Types.string {
    description: 'Cluster Name',
    enum: [
      'N/A',
      'RESEARCH AND DEVELOPMENT',
      'STUDENT FINANCIAL ASSISTANCE',
      Const.STATE_CLUSTER,
      '477 CLUSTER',
      'AGING CLUSTER',
      'CCDF CLUSTER',
      'CDBG - DISASTER RECOVERY GRANTS - PUB. L. NO. 113-2 CLUSTER',
      'CDBG - ENTITLEMENT GRANTS CLUSTER',
      'CDFI CLUSTER',
      'CHILD NUTRITION CLUSTER',
      'CLEAN WATER STATE REVOLVING FUND CLUSTER',
      'COMMUNITY FACILITIES LOANS AND GRANTS CLUSTER',
      'DISABILITY INSURANCE/SSI CLUSTER',
      'DRINKING WATER STATE REVOLVING FUND CLUSTER',
      'ECONOMIC DEVELOPMENT CLUSTER',
      'EMPLOYMENT SERVICE CLUSTER',
      'FEDERAL TRANSIT CLUSTER',
      'FISH AND WILDLIFE CLUSTER',
      'FOOD DISTRIBUTION CLUSTER',
      'FOREIGN FOOD AID DONATION CLUSTER',
      'FOREST SERVICE SCHOOLS AND ROADS CLUSTER',
      'FOSTER GRANDPARENT/SENIOR COMPANION CLUSTER',
      'HEAD START CLUSTER',
      'HEALTH CENTER PROGRAM CLUSTER',
      'HIGHWAY PLANNING AND CONSTRUCTION CLUSTER',
      'HIGHWAY SAFETY CLUSTER',
      'HOPE VI CLUSTER',
      'HOUSING VOUCHER CLUSTER',
      'HURRICANE SANDY RELIEF CLUSTER',
      'MATERNAL, INFANT, AND EARLY CHILDHOOD HOME VISITING CLUSTER',
      'MEDICAID CLUSTER',
      'SCHOOL IMPROVEMENT GRANTS CLUSTER',
      'SECTION 8 PROJECT-BASED CLUSTER',
      'SNAP CLUSTER',
      'SPECIAL EDUCATION CLUSTER (IDEA)',
      'TANF CLUSTER',
      'TRANSIT SERVICES PROGRAMS CLUSTER',
      'TRIO CLUSTER',
      'WATER AND WASTE PROGRAM CLUSTER',
      'WIOA CLUSTER',
      Const.OTHER_CLUSTER,
    ],
    title: 'ClusterName',
  },
 
  NonEmptyString: Types.string {
      minLength: 1
  },
  StateClusterNameNonAnswers: Enum.EmptyString_Null,

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
  Compound: Compound,
  SchemaBase: SchemaBase,
}
