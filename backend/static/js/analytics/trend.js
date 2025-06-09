import Plotly from 'plotly.js-dist';

// Pull the data from the Django template tag passthrough
var api_data = JSON.parse(
  document.getElementById('dashboard_data').textContent
);

const state = api_data.state;
const combined_years = api_data.combined_years;
api_data = api_data.trend_analytics;

var config = { responsive: true };

/**
 * TOTAL AWARD VOLUME
 * Scatter plot, one point per year
 */
var data_total_award_volume = api_data.total_award_volume;
var chart_data_total_award_volume = [
  {
    x: data_total_award_volume.map((object) => object.year),
    y: data_total_award_volume.map((object) => object.total),
    text: data_total_award_volume.map((object) =>
      new Intl.NumberFormat('en-US', { currency: "USD", maximumSignificantDigits: 3, style: "currency"}).format(
        object.total
      )
    ),
    textposition: 'outside',
    marker: {
      // color: '#152973',  // FAC logo dark blue
      color: '#56B833', // FAC logo green
      width: 1,
    },
    type: 'bar',
  },
];
var chart_layout_total_award_volume = {
  title: {
    text: `Total Award Volume - State: ${state}, Years: ${combined_years}`,
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Dollars',
    },
  },
  autosize: true,
}

Plotly.newPlot(
  'div_total_award_volume',
  chart_data_total_award_volume,
  chart_layout_total_award_volume,
  config
);

/**
 * TOTAL FINDINGS
 * Scatter plot, one point per year
 */
var data_total_findings = api_data.total_findings;
console.log(api_data.total_findings)
var chart_data_total_findings = [
  {
    x: data_total_findings.map((object) => object.year),
    y: data_total_findings.map((object) => object.total),
    text: data_total_findings.map((object) =>
      new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3 }).format(
        object.total
      )
    ),
    textposition: 'outside',
    marker: {
      color: '#152973', // FAC logo dark blue
      // color: '#56B833', // FAC logo green
      width: 1,
    },
    type: 'bar',
  },
];
var chart_layout_total_findings = {
  title: {
    text: `Total Findings - State: ${state}, Years: ${combined_years}`,
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Findings',
    },
  },
};

Plotly.newPlot(
  'div_total_findings',
  chart_data_total_findings,
  chart_layout_total_findings,
  config
);

/**
 * SUBMISSIONS WITH FINDINGS
 * Scatter plot, one point per year
 */
var data_submissions_with_findings = api_data.submissions_with_findings;
var chart_data_submissions_with_findings = [
  {
    x: data_submissions_with_findings.map((object) => object.year),
    y: data_submissions_with_findings.map((object) => object.total),
    text: data_total_findings.map((object) =>
      new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3 }).format(
        object.total
      )
    ),
    textposition: 'outside',
    marker: {
      // color: '#152973', // FAC logo dark blue
      color: '#56B833', // FAC logo green
      width: 1,
    },
    type: 'bar',
  },
];
var chart_layout_submissions_with_findings = {
  title: {
    text: `Total Submissions with Findings - State: ${state}, Years: ${combined_years}`,
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Submissions',
    },
    tickformat: '.0f', // Enforce integer values
  },
};

Plotly.newPlot(
  'div_total_submissions_with_findings',
  chart_data_submissions_with_findings,
  chart_layout_submissions_with_findings,
  config
);
