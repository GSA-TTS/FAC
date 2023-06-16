local scheme = 'https';
local domain = 'fac.gov';
local path = 'documentation/validation';

local make_url = function(anchor)
  scheme + '://' + domain + '/' + path + '/#' + anchor;

{
  // A
  aln_extension: {
    text: '',
    link: make_url('aln_extension'),
  },
  aln_prefix: {
    text: '',
    link: make_url('aln_prefix'),
  },
  // C
  cluster_name: {
    text: '',
    link: make_url('cluster_name'),
  },
  // F
  federal_program_name: {
    text: '',
    link: make_url('federal_program_name'),
  },
  // O
  other_cluster_name: {
    text: '',
    link: make_url('other_cluster_name'),
  },
  // P
  plain_text: {
    text: '',
    link: make_url('plain_text'),
  },
  positive_number: {
    text: '',
    link: make_url('positive_number'),
  },
  // R
  reference_number: {
    text: '',
    link: make_url('reference_number'),
  },
  // U
  uei: {
    text: '',
    link: make_url('uei'),
  },
  unknown: {
    text: 'If you see this error, please contact support.',
    link: make_url('unknown'),
  },
  // Y
  yorn: {
    text: '',
    link: make_url('yorn'),
  },

}
