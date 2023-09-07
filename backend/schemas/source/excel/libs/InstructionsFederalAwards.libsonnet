{
  federal_agency_prefix: {
    instructions: [
      'Enter the first two digits of the agency\'s CFDA number.',
    ],
  },
  three_digit_extension: {
    instructions: [
      'Enter the last three digits of the agency\'s CFDA number.',
      'For programs with No CFDA Number or if the CDFA Number is Unknown, enter a "U" followed by a two-digit number in the CFDA extension to identify one or more Federal award lines that form the program.',
      'If the Federal program is part of the Research and Development (R&D) cluster and the three-digit CFDA extension is unknown, enter "RD" in the CFDA Three-Digit Extension field.',
      'If the Federal program is part of the R&D cluster and the CFDA Three-Digit Extension is known, enter the CFDA Three-Digit Extension.'
    ],
  },
  additional_award_identification: {
    instructions: [
      'Enter non-CFDA identifying data for the award (e.g., program year, contract number, state issued numbers, etc.).',
      'This field is required if you don\'t know the agency\'s CFDA extension. If you entered a valid extension in the previous field, this field can be left blank.'
    ],
  },
  program_name: {
    instructions: [
      'Enter the name of the Federal program as shown in the CFDA. If the program is not listed in the CFDA, enter a description of the award recognizable by the Federal awarding agency or pass-through entity.',
    ],
  },
  amount_expended: {
    instructions: [
      'Enter the amount of expenditures for each Federal award.',
    ],
  },
  cluster_name: {
    instructions: [
      'Select the name of the cluster of programs using the drop-down menu.',
      'If the program is not part of a cluster, select "N/A" for no cluster.',
      'If the cluster name is not on the drop-down list, select "Other Cluster Not Listed Above".',
    ],
  },
  state_cluster_name: {
    instructions: [
      'If the program is part of a state cluster, enter the State Cluster name. If the program is not part of a state cluster, leave this blank.',
    ],
  },
  other_cluster_name: {
    instructions: [
      'If you selected "Other Cluster Not Listed Above" in the Cluster Name field, enter the cluster name here.',
    ],
  },
  federal_program_total: {
    instructions: [
      'This field is auto-completed based on previous field responses.',
    ],
  },
  cluster_total: {
    instructions: [
      'This field is auto-completed based on previous field responses.',
    ],
  },
  is_guaranteed: {
    instructions: [
      'Select "Y" if the program is a Federal loan or a Federal loan guarantee. If not, select "N".',
    ],
  },
  loan_balance_at_audit_period_end: {
    instructions: [
      'If the program is a Federal loan or a Federal loan guarantee, enter the loan or loan guarantee balance outstanding at the end of the audit period.',
      'If the outstanding loan balance is not applicable, enter "N/A".'
    ],
  },
  is_direct: {
    instructions: [
      'Select "Y" if the award came directly from a Federal awarding agency. If not, select "N".',
    ],
  },
  passthrough_name: {
    instructions: [
      'If the award did not come directly from a Federal awarding agency,enter the name of the pass-through entity.',
    ],
  },
  passthrough_identifying_number: {
    instructions: [
      'If the award did not come directly from a Federal awarding agency, enter the identifying number assigned by the pass-through entity.',
      'If there is not an identifying number assigned by the pass-through entity, enter "N/A" in this field.'
    ],
  },
  is_passed: {
    instructions: [
      'Select "Y" if the auditee entity passed on the Federal award to a subrecpient. If not, select "N".',
      'Direct awards transferred within departments of the auditee entity are not considered passthrough funds.',
    ],
  },
  subrecipient_amount: {
    instructions: [
      'Enter the amount passed through to the subrecipient.',
    ],
  },
  is_major: {
    instructions: [
      'Select "Y" if the Federal program is a major program, as defined in 2 CFR 200.518. If not, select "N".',
    ],
  },
  audit_report_type: {
    instructions: [
      'If the Federal program is a major program, enter the letter (U, Q, A, or D) for the type of audit report on the major program.',
      '"U" for Unmodified opinion',
      '"Q" for Qualified opinion',
      '"A" for Adverse opinion',
      '"D" for Disclaimer of opinion',
      'The type of audit report applies to all programs in a cluster. For clusters, enter the same letter for all programs in each.',
      'If a CFDA number has multiple lines, each line must have the same major program determination and type of audit report.',
      'If the program is not a major program, leave this field blank.'
    ],
  },
  number_of_audit_findings: {
    instructions: [
      'Enter the number of audit findings for each Federal program. If there are no audit findings, enter "0" (zero).',
      'If the type of audit report is "Adverse opinion" or "Qualified opinion", this field cannot be 0 (zero).',
    ],
  },
}
