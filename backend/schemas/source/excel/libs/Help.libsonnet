local scheme = 'https';
local domain = 'fac.gov';
local path = 'documentation/validation';

local make_url = function(anchor)
  scheme + '://' + domain + '/' + path + '/#' + anchor;

{
  // A
  aln_extension: {
    text: 'An ALN (CFDA) extension is typically three digits, with some exceptions',
    link: make_url('aln_extension'),
  },
  aln_prefix: {
    text: 'Not a valid agency ALN (CFDA) prefix',
    link: make_url('aln_prefix'),
  },
  // A
  award_reference: {
    text: 'Award reference have the form AWARD-NNNN (e.g. AWARD-0001)',
    link: make_url('award_reference'),
  },
  // C
  cluster_name: {
    text: 'Not one of the allowed cluster names',
    link: make_url('cluster_name'),
  },
  ein: {
    text: 'Employer identification numbers (EIN) are nine characters long and match rules given by the IRS',
    link: make_url('ein'),
  },
  // F
  federal_program_name: {
    text: 'Not one of the allowed federal program names',
    link: make_url('federal_program_name'),
  },
  // O
  other_cluster_name: {
    text: 'Not one of the alternative (other) cluster names',
    link: make_url('other_cluster_name'),
  },
  // P
  plain_text: {
    text: 'Only plain text is allowed in this field, no emoji or other special additions',
    link: make_url('plain_text'),
  },
  positive_number: {
    text: 'The number in this field must be zero or greater',
    link: make_url('positive_number'),
  },
  // R
  reference_number: {
    text: 'Reference numbers have the form YYYY-NNN (e.g. 2023-001)',
    link: make_url('reference_number'),
  },
  // U
  uei: {
    text: 'UEIs are 12 characters long and match rules as given by SAM.gov',
    link: make_url('uei'),
  },
  unknown: {
    text: 'If you see this error, please contact support.',
    link: make_url('unknown'),
  },
  // Y
  yorn: {
    text: 'This field must be either `Y` or `N`',
    link: make_url('yorn'),
  },

}
