local scheme = 'https';
local domain = 'fac.gov';
local path = 'documentation/validation';

local make_url = function(anchor)
  scheme + '://' + domain + '/' + path + '/#' + anchor;

{
  // A
  aln_extension: {
    text: 'An ALN (CFDA) extension is typically three digits, with some exceptions. If unknown extension, enter "UNN" (e.g. U01, U02, U03, etc.). For research and development, enter "RD"',
    link: make_url('aln_extension'),
  },
  aln_prefix: {
    text: 'Invalid agency ALN (CFDA) prefix',
    link: make_url('aln_prefix'),
  },
  // A
  award_reference: {
    text: 'Award reference have the form AWARD-NNNN (e.g. AWARD-0001)',
    link: make_url('award_reference'),
  },
  // C
  cluster_name: {
    text: 'Select from the approved cluster names',
    link: make_url('cluster_name'),
  },
  ein: {
    text: 'Employer identification numbers (EIN) are nine characters long and match rules given by the IRS',
    link: make_url('ein'),
  },
  // F
  federal_program_name: {
    text: 'Select from the approved federal program names',
    link: make_url('federal_program_name'),
  },
  // O
  other_cluster_name: {
    text: 'Name must be 75 characters or less',
    link: make_url('other_cluster_name'),
  },
  // P
  plain_text: {
    text: 'Only plain text is allowed, no emoji, formatting, or other special additions',
    link: make_url('plain_text'),
  },
  positive_number: {
    text: 'The number must be zero or greater',
    link: make_url('positive_number'),
  },
  any_number: {
    text: 'Must be a number',
    link: make_url('any_number'),
  },
  prior_references: {
    text: 'Must be a comma-separated list of reference numbers (YYYY-NNN) or N/A.',
    link: make_url('prior_references'),
  },
  // R
  reference_number: {
    text: 'Reference numbers must be formatted YYYY-NNN (e.g. 2023-001)',
    link: make_url('reference_number'),
  },
  // U
  uei: {
    text: 'UEIs are 12 characters long and match rules as given by SAM.gov',
    link: make_url('uei'),
  },
  unknown: {
    text: 'Please contact support',
    link: make_url('unknown'),
  },
  // Y
  yorn: {
    text: 'This field must be either `Y` or `N`',
    link: make_url('yorn'),
  },
  yornorboth: {
    text: 'This field must be either `Y`, `N`, or `Both`',
    link: make_url('yornorboth'),
  },
  // w
  wrong_workbook_template: {
    text: 'The workbook you tried to upload is for a different section.',
    link: make_url('section_name'),
  },
}
