import Plotly from 'plotly.js-dist'

// Pull the data from the Django template tag passthrough
var api_data = JSON.parse(document.getElementById('dashboard_data').textContent)

var config = {responsive: true}

/**
 * FUNDING BY ENTITY TYPE
 * Pie chart, six sections
 */
var data_entity_type = api_data.funding_by_entity_type
var chart_data_entity_type = [
  {
    labels: data_entity_type.map(object => object.entity_type),
    values: data_entity_type.map(object => object.total_expended),
    hoverinfo: 'label+percent',
    hole: 0.4,
    type: 'pie',
  }
];
var chart_layout_entity_type = {
  title: {
    text: 'Funding By Entity Type',
  },
  height: 400,
  width: 600,
  showlegend: true,
  grid: { rows: 1, columns: 1}
}

Plotly.newPlot('div_entity_type', chart_data_entity_type, chart_layout_entity_type, config)


/**
 * PROGRAMS WITH REPEATED FINDINGS
 * Bar chart, X programs by entity count
 */
var data_repeated_findings = api_data.programs_with_repeated_findings
var chart_data_repeated_findings = [
  {
    x: data_repeated_findings.map(object => object.repeat_findings),
    y: data_repeated_findings.map(object => object.award_name),
    orientation: 'h',
    name: 'Number of Entities',
    marker: {
      // color: '#152973',  // FAC logo dark blue
      color: '#56B833',  // FAC logo green
      width: 1
    },
    type: 'bar'
  }
]
var chart_layout_repeated_findings = {
  title: {
    text: 'Programs With Repeated Findings',
  },
  height: 400,
  width: 600,
  showlegend: true,
  grid: { rows: 1, columns: 1}
}

Plotly.newPlot('div_repeated_findings', chart_data_repeated_findings, chart_layout_repeated_findings, config)

/**
 * TOP PROGRAMS
 * Bar chart, top X programs
 */
var data_top_programs = api_data.top_programs
console.log(data_top_programs)
var chart_data_top_programs = [
  {
    x: data_top_programs.map(object => object.total_expended),
    y: data_top_programs.map(object => object.federal_program_name),
    orientation: 'h',
    name: 'Dollars (Billions)',
    marker: {
      color: '#152973',  // FAC logo dark blue
      // color: '#56B833',  // FAC logo green
      width: 1
    },
    type: 'bar'
  }
]
var chart_layout_top_programs = {
  title: {
    text: 'Top Programs',
  },
  height: 400,
  width: 600,
  showlegend: true,
  grid: { rows: 1, columns: 1}
};

Plotly.newPlot('div_top_programs', chart_data_top_programs, chart_layout_top_programs, config);
