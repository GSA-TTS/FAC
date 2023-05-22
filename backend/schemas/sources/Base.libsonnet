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

local Validation = {
  AdditionalAwardIdentificationValidation: [
    {
      "if": {
        properties: {
          three_digit_extension: {
            pattern: '^(RD|U[0-9]{2})$',
          },
          },
      },
      "then": {
        properties: {
          additional_award_identification: Types.string{
            minLength: 1,
          },
        },
        required: ['additional_award_identification'] 
      },
    },   
  ],
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
  ALNPrefixes: Types.string {
    description: 'Valid two-digit program numbers; part of the CFDA/ALN',
    enum: [
      '1',
      '2',
      '3',
      '4',
      '7',
      '8',
      '9',
      '10',
      '11',
      '12',
      '13',
      '14',
      '15',
      '16',
      '17',
      '18',
      '19',
      '20',
      '21',
      '22',
      '23',
      '27',
      '29',
      '30',
      '32',
      '33',
      '34',
      '36',
      '39',
      '40',
      '41',
      '42',
      '43',
      '44',
      '45',
      '46',
      '47',
      '53',
      '57',
      '58',
      '59',
      '60',
      '61',
      '62',
      '64',
      '66',
      '68',
      '70',
      '77',
      '78',
      '81',
      '82',
      '83',
      '84',
      '85',
      '86',
      '87',
      '88',
      '89',
      '90',
      '91',
      '92',
      '93',
      '94',
      '96',
      '97',
      '98',
    ],
  },
};

local Compound = {
  ThreeDigitExtension: Types.string {
    title: 'ThreeDigitExtension',
    description: 'Three Digit Extension',
    pattern: '^(RD|[0-9]{3}[A-Za-z]{0,1}|U[0-9]{2})$',
  },  
  PriorReferences: Types.string {
    title: 'PriorReferences',
    description: 'Prior references',
    pattern: '^20[2-9][0-9]-[0-9]{3}(,\\s*20[2-9][0-9]-[0-9]{3})*$',
  },
  ReferenceNumber: Types.string {
    title: 'ReferenceNumber',
    description: 'Reference Number',
    pattern: '^20[2-9][0-9]-[0-9]{3}$',
  },
  ComplianceRequirement: {
    title: 'ComplianceRequirement',
    description: 'Compliance requirement type',
    pattern: '^A?B?C?E?F?G?H?I?J?L?M?N?P?$',
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
    minLength: 1,
  },
  StateClusterNameNonAnswers: Enum.EmptyString_Null,
  EmployerIdentificationNumber: Types.string {
      pattern: "^[0-9]{9}$",
  },
  UniqueEntityIdentifier: Types.string {
      pattern: "^$|^[a-hj-np-zA-HJ-NP-Z1-9][a-hj-np-zA-HJ-NP-Z0-9]{11}$",
  }

};

local REGEX_ZIPCODE = '^[0-9]{5}([0-9]{4})?$';
local REGEX_DBKEY = '[1-9][0-9]+';

local type_zipcode = Types.string {
  pattern: REGEX_ZIPCODE,
};


local type_string_or_null = {
  oneOf: [
    Types.NULL,
    Types.string,
  ],
};

// No capital I or O, but lowercase is fine? FIXME check...
local REGEX_UEI_ALPHA = 'A-H,J-N,P-Z,a-z';
local REGEX_UEI_LEADING_CLOISTER = '[' + REGEX_UEI_ALPHA + ',1-9]';
local REGEX_UEI_BODY_CLOISTER = '[' + REGEX_UEI_ALPHA + ',0-9]';

// This may not be a *complete* UEI validator.
// However, it is a start of one. The UEI rules are broken
// out so that all of the rules must apply.
local type_uei = Types.string {
  allOf: [
    // Is a string
    {
      minLength: 12,
      maxLength: 12,
    },
    // Is alphanumeric, but no I or O
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
  ],
};

local phone_regex = '[1-9]{1}[0-9]{9}+';
local e164_regex = '^\\+[0-9]{1,3}[ ]*[0-9]{2,3}[ ]*[0-9]{2,3}[ ]*[0-9]{4}|^\\+[0-9]{1,3}[ ]*[0-9]{1,14}([ ]*[0-9]{1,13})?|^\\([0-9]{3}\\)[ ]*[0-9]{3}[ ]*[0-9]{4}?';
local email_regex = '^[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\\.[a-zA-Z0-9!#$%&\'*+/=?^_`{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?$';


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
  Compound: Compound + {
    UEI: type_uei
  },
  Validation: Validation,
  SchemaBase: SchemaBase,
}
