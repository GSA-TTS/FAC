/**
 * Field mappings for displayed charts.
 */

export const state_fields_mapping = {
  funding_by_entity_type: {
    div_name: 'div_entity_type',
    field_name: 'funding_by_entity_type',
    friendly_name: 'Funding By Entity Type',
  },
  programs_with_repeated_findings: {
    div_name: 'div_repeated_findings',
    field_name: 'programs_with_repeated_findings',
    friendly_name: 'Programs With Repeated Findings',
    trace1_friendly_name: 'Number of Entities',
    minreducedwidth: 400, // Limit length of y axis values so the chart doesn't get too small
  },
  top_programs: {
    div_name: 'div_top_programs',
    field_name: 'top_programs',
    friendly_name: 'Top Programs',
    trace1_friendly_name: 'Dollars',
    minreducedwidth: 400, // Limit length of y axis values so the chart doesn't get too small
  },
};

export const trend_fields_mapping = {
  total_submissions: {
    div_name: 'div_total_submissions',
    field_name: 'total_submissions',
    friendly_name: 'Total Submissions',
    x_axis_label: 'Year',
    y_axis_label: 'Count',
  },
  total_award_volume: {
    div_name: 'div_total_award_volume',
    field_name: 'total_award_volume',
    friendly_name: 'Total Award Volume',
    x_axis_label: 'Year',
    y_axis_label: 'Amount (USD)',
  },
  total_findings: {
    div_name: 'div_total_findings',
    field_name: 'total_findings',
    friendly_name: 'Total Findings',
    x_axis_label: 'Year',
    y_axis_label: 'Count',
  },
  percent_submissions_with_findings: {
    div_name: 'div_submissions_with_findings',
    field_name: 'submissions_with_findings',
    friendly_name: '% Submissions with Findings',
    x_axis_label: 'Year',
    y_axis_label: 'Percentage',
  },
  percent_auditee_risk_profile: {
    div_name: 'div_auditee_risk_profile',
    field_name: 'auditee_risk_profile',
    friendly_name: 'Auditee Risk Profile',
    // Pie charts use labels instead of axes
    section_labels: ['Low Risk', 'Not Low Risk'],
  },
  risk_profile_vs_findings: {
    div_name: 'div_risk_profile_vs_findings',
    field_name: 'risk_profile_vs_findings',
    friendly_name: '% Not Low-Risk vs % With Findings by Year',
    // Contains two traces to compare the two values.
    trace1_friendly_name: '% Not Low-Risk Auditees',
    trace2_friendly_name: '% Submissions With Findings',
    x_axis_label: 'Year',
    y_axis_label: 'Percentage',
  },
};
