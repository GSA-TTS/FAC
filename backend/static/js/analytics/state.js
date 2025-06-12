import Plotly from 'plotly.js-dist';

// Pull the data from the Django template tag passthrough
var api_data = JSON.parse(
  document.getElementById('dashboard_data').textContent
);

const state = api_data.state;
const year = api_data.year;
api_data = api_data.state_analytics;

var config = { responsive: true };

/**
 * FUNDING BY ENTITY TYPE
 * Pie chart, six sections
 */
var data_entity_type = api_data.funding_by_entity_type;
var chart_data_entity_type = [
  {
    labels: data_entity_type.map((object) => object.entity_type),
    values: data_entity_type.map((object) => object.total_expended),
    hoverinfo: 'label+percent',
    hole: 0.4, // Donut style
    type: 'pie',
  },
];
var chart_layout_entity_type = {
  title: {
    text: `Funding By Entity Type - State: ${state}, Year: ${year}`,
  },
  showlegend: true,
};

Plotly.newPlot(
  'div_entity_type',
  chart_data_entity_type,
  chart_layout_entity_type,
  config
);

/**
 * PROGRAMS WITH REPEATED FINDINGS
 * Bar chart, X programs by entity count
 */
var data_repeated_findings = api_data.programs_with_repeated_findings;
var chart_data_repeated_findings = [
  {
    x: data_repeated_findings.reverse().map((object) => object.repeat_findings),
    y: data_repeated_findings
      .reverse()
      .map((object) => object.federal_program_name),
    orientation: 'h',
    name: 'Number of Entities',
    marker: {
      // color: '#152973',  // FAC logo dark blue
      color: '#56B833', // FAC logo green
      width: 1,
    },
    type: 'bar',
  },
];
var chart_layout_repeated_findings = {
  title: {
    text: `Programs With Repeated Findings - State: ${state}, Year: ${year}`,
  },
  showlegend: true,
  yaxis: { automargin: true },
  minreducedwidth: 400,
};

Plotly.newPlot(
  'div_repeated_findings',
  chart_data_repeated_findings,
  chart_layout_repeated_findings,
  config
);

/**
 * TOP PROGRAMS
 * Bar chart, top X programs
 */
var data_top_programs = api_data.top_programs;
var chart_data_top_programs = [
  {
    x: data_top_programs.reverse().map((object) => object.total_expended),
    y: data_top_programs.reverse().map((object) => object.federal_program_name),
    orientation: 'h',
    name: 'Dollars',
    marker: {
      color: '#152973', // FAC logo dark blue
      // color: '#56B833',  // FAC logo green
      width: 1,
    },
    type: 'bar',
  },
];
var chart_layout_top_programs = {
  title: {
    text: `Top Programs - State: ${state}, Year: ${year}`,
  },
  showlegend: true,
  yaxis: { automargin: true },
  minreducedwidth: 400,
};

Plotly.newPlot(
  'div_top_programs',
  chart_data_top_programs,
  chart_layout_top_programs,
  config
);
