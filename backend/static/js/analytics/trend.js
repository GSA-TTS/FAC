import Plotly from 'plotly.js-strict-dist';
import { trend_fields_mapping } from './field_mappings';

// Pull the data from the Django template tag passthrough
var api_data = JSON.parse(
  document.getElementById('dashboard_data').textContent
);
api_data = api_data.trend_analytics;

const config = { responsive: true };

/**
 * Draws a bar chart for total submissions. One bar per year.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_total_submissions(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [
    {
      x: data.map((object) => object.year),
      y: data.map((object) => object.total),
      text: data.map((object) =>
        new Intl.NumberFormat('en-US').format(object.total)
      ),
      textposition: 'outside',
      marker: {
        color: '#56B833', // FAC logo green
        width: 1,
      },
      type: 'bar',
    },
  ];
  var chart_layout = {
    title: {
      text: mapping.friendly_name,
    },
    margin: {
      t: 25,
    },
    xaxis: {
      title: {
        text: mapping.x_axis_label,
      },
      type: 'category',
    },
    yaxis: {
      title: {
        text: mapping.y_axis_label,
      },
    },
    autosize: true,
  };
  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

/**
 * Draws a bar chart for total award volume. One bar per year.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_total_award_volume(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [
    {
      x: data.map((object) => object.year),
      y: data.map((object) => object.total),
      text: data.map((object) =>
        new Intl.NumberFormat('en-US', {
          currency: 'USD',
          maximumSignificantDigits: 6,
          style: 'currency',
        }).format(object.total)
      ),
      textposition: 'outside',
      marker: {
        color: '#152973', // FAC logo dark blue
        width: 1,
      },
      type: 'bar',
    },
  ];
  var chart_layout = {
    title: {
      text: mapping.friendly_name,
    },
    margin: {
      t: 25,
    },
    xaxis: {
      title: {
        text: mapping.x_axis_label,
      },
      type: 'category',
    },
    yaxis: {
      title: {
        text: mapping.y_axis_label,
      },
    },
    autosize: true,
  };

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

/**
 * Draws a bar chart for total findings. One bar per year.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_total_findings(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [
    {
      x: data.map((object) => object.year),
      y: data.map((object) => object.total),
      text: data.map((object) =>
        new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3 }).format(
          object.total
        )
      ),
      textposition: 'outside',
      marker: {
        color: '#152973', // FAC logo dark blue
        width: 1,
      },
      type: 'bar',
    },
  ];
  var chart_layout = {
    title: {
      text: mapping.friendly_name,
    },
    margin: {
      t: 25,
    },
    xaxis: {
      title: {
        text: mapping.x_axis_label,
      },
      type: 'category',
    },
    yaxis: {
      title: {
        text: mapping.y_axis_label,
      },
    },
  };

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

/**
 * Draws a bar chart for the percent of submissions with findings. One bar per year.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_percent_submissions_with_findings(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [
    {
      x: data.map((object) => object.year),
      y: data.map((object) => object.total),
      text: data.map(
        (object) =>
          new Intl.NumberFormat('en-US', {
            maximumSignificantDigits: 3,
          }).format(object.total) + '%'
      ),
      textposition: 'outside',
      marker: {
        color: '#56B833', // FAC logo green
        width: 1,
      },
      type: 'bar',
    },
  ];
  var chart_layout = {
    title: {
      text: mapping.friendly_name,
    },
    margin: {
      t: 25,
    },
    xaxis: {
      title: {
        text: mapping.x_axis_label,
      },
      type: 'category',
    },
    yaxis: {
      title: {
        text: mapping.y_axis_label,
      },
      ticksuffix: '%',
    },
  };

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

/**
 * Draws a pie chart for the percent of submissions with findings. One chart per year as subplots.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_auditee_risk_profile(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [];
  data.forEach((object, index) =>
    chart_data.push({
      labels: mapping.section_labels,
      values: [object.low_risk, object.not_low_risk],
      name: object.year,
      hoverinfo: 'label+percent',
      type: 'pie',
      domain: {
        row: Math.floor(index / 2),
        column: index % 2,
      },
    })
  );
  var chart_layout = {
    title: {
      text: mapping.friendly_name,
    },
    annotations: [], // Populated dynamically below
    // 'autosize' doesn't seem to work with subplots.
    height: 450 + 150 * (data.length - 2),
    width: 850,
    autosize: true,
    grid: { rows: Math.ceil(data.length / 2), columns: 2 },
    showlegend: true,
  };
  // Note: The pie charts should all become their own charts, not subplots, in order to title them properly.
  // This is a strange solution to annotate each chart with the appropriate title.
  data.forEach((object, index) =>
    chart_layout.annotations.push({
      text: object.year,
      showarrow: false,
      x: index % 2 ? 0.77 : 0.24,
      xref: 'paper',
      xanchor: 'center',
      y: 1.006 - Math.floor(index / 2) / Math.ceil(data.length / 2),
      yref: 'paper',
      yanchor: Math.floor(index / 2) ? 'top' : 'bottom',
    })
  );

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

/**
 * Draws a bar chart to compare risk profile and findings. Two bars per year, and therefore two traces.
 * @param {object} mapping Field and friendly names for the chart pieces.
 */
function draw_risk_profile_vs_findings(mapping) {
  var data = api_data[mapping.field_name];

  if (data.length == 0) return;

  var chart_data = [
    // Trace one, % not low risk
    {
      x: data.map((object) => object.year),
      y: data.map((object) => object.not_low_risk),
      text: data.map(
        (object) =>
          new Intl.NumberFormat('en-US', {
            maximumSignificantDigits: 3,
          }).format(object.not_low_risk) + '%'
      ),
      textposition: 'outside',
      marker: {
        color: '#56B833', // FAC logo green
        width: 1,
      },
      name: mapping.trace1_friendly_name,
      type: 'bar',
    },
    // Trace two, % submissions with findings
    {
      x: data.map((object) => object.year),
      y: data.map((object) => object.audits_with_findings),
      text: data.map(
        (object) =>
          new Intl.NumberFormat('en-US', {
            maximumSignificantDigits: 3,
          }).format(object.audits_with_findings) + '%'
      ),
      textposition: 'outside',
      marker: {
        color: '#152973', // FAC logo dark blue
        width: 1,
      },
      name: mapping.trace2_friendly_name,
      type: 'bar',
    },
  ];
  var chart_layout = {
    title: {
      text: mapping.friendly_name,
    },
    margin: {
      t: 25,
    },
    xaxis: {
      title: {
        text: mapping.x_axis_label,
      },
      type: 'category',
    },
    yaxis: {
      title: {
        text: mapping.y_axis_label,
      },
      ticksuffix: '%',
    },
  };

  Plotly.newPlot(mapping.div_name, chart_data, chart_layout, config);
}

function init() {
  draw_total_submissions(trend_fields_mapping.total_submissions);
  draw_total_award_volume(trend_fields_mapping.total_award_volume);
  draw_total_findings(trend_fields_mapping.total_findings);
  draw_percent_submissions_with_findings(
    trend_fields_mapping.percent_submissions_with_findings
  );
  draw_auditee_risk_profile(trend_fields_mapping.percent_auditee_risk_profile);
  draw_risk_profile_vs_findings(trend_fields_mapping.risk_profile_vs_findings);
}

init();
