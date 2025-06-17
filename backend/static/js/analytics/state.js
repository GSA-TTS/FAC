import Plotly from 'plotly.js-strict-dist';
import { state_fields_mapping } from './field_mappings';

// Pull the data from the Django template tag passthrough
var api_data = JSON.parse(
  document.getElementById('dashboard_data').textContent
);

const state = api_data.state;
const year = api_data.year;
api_data = api_data.state_analytics;

var config = { responsive: true };

/**
 * Draws a pie chart for finding by entity type. Up to six sections.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_funding_by_entity_type(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  const label_mapping = {
    'state': 'State',
    'local': 'Local Government',
    'tribal': 'Indian tribe or tribal organization',
    'higher-ed': 'Institution of Higher Education (IHE)',
    'non-profit': 'Non-profit',
    'unknown': 'Unknown',
  };
  var chart_data = [
    {
      labels: data.map((object) => label_mapping[object.entity_type]),
      values: data.map((object) => object.total_expended),
      hoverinfo: 'label+percent',
      hole: 0.4, // Donut style
      type: 'pie',
    },
  ];
  var chart_layout = {
    title: {
      text: `${mapping.friendly_name} - State: ${state}, Year: ${year}`,
    },
    showlegend: true,
  };

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

/**
 * Draws a horizontal bar chart for top entities by repeated findings count.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_programs_with_repeated_findings(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [
    {
      x: data.reverse().map((object) => object.repeat_findings),
      y: data.reverse().map((object) => object.federal_program_name),
      orientation: 'h',
      name: mapping.trace1_friendly_name,
      marker: {
        color: '#56B833', // FAC logo green
        width: 1,
      },
      type: 'bar',
    },
  ];
  var chart_layout = {
    title: {
      text: `${mapping.friendly_name} - State: ${state}, Year: ${year}`,
    },
    showlegend: true,
    yaxis: { automargin: true },
    minreducedwidth: mapping.minreducedwidth,
  };

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

/**
 * Draws a horizontal bar chart for top programs by dollar amount.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_top_programs(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [
    {
      x: data.reverse().map((object) => object.total_expended),
      y: data.reverse().map((object) => object.federal_program_name),
      orientation: 'h',
      name: 'Dollars',
      marker: {
        color: '#152973', // FAC logo dark blue
        width: 1,
      },
      type: 'bar',
    },
  ];
  var chart_layout = {
    title: {
      text: `${mapping.friendly_name} - State: ${state}, Year: ${year}`,
    },
    showlegend: true,
    yaxis: { automargin: true },
    minreducedwidth: mapping.minreducedwidth,
  };

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

function init() {
  draw_funding_by_entity_type(state_fields_mapping.funding_by_entity_type);
  draw_programs_with_repeated_findings(
    state_fields_mapping.programs_with_repeated_findings
  );
  draw_top_programs(state_fields_mapping.top_programs);
}

init();
