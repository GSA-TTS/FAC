import Plotly from 'plotly.js-dist'

// Pull the data from the Django template tag passthrough
var api_data = JSON.parse(
  document.getElementById('dashboard_data').textContent
)

api_data = api_data.trend_analytics

var config = { responsive: true }

/**
 * TOTAL SUBMISSIONS
 * Bar chart, one bar per year
 */
var data_total_submissions = api_data.total_submissions
var chart_data_total_submissions = [
  {
    x: data_total_submissions.map((object) => object.year),
    y: data_total_submissions.map((object) => object.total),
    text: data_total_submissions.map((object) =>
      new Intl.NumberFormat('en-US').format(
        object.total
      )
    ),
    textposition: 'outside',
    marker: {
      color: '#56B833', // FAC logo green
      width: 1,
    },
    type: 'bar',
  },
]
var chart_layout_total_submissions = {
  title: {
    text: 'Total Submissions',
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Count',
    },
  },
  autosize: true,
}
Plotly.newPlot(
  'div_total_submissions',
  chart_data_total_submissions,
  chart_layout_total_submissions,
  config
)

/**
 * TOTAL AWARD VOLUME
 * Bar chart, one bar per year
 */
var data_total_award_volume = api_data.total_award_volume
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
      color: '#152973',  // FAC logo dark blue
      width: 1,
    },
    type: 'bar',
  },
]
var chart_layout_total_award_volume = {
  title: {
    text: 'Total Award Volume',
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Amount (USD)',
    },
  },
  autosize: true,
}

Plotly.newPlot(
  'div_total_award_volume',
  chart_data_total_award_volume,
  chart_layout_total_award_volume,
  config
)

/**
 * TOTAL FINDINGS
 * Bar chart, one bar per year
 */
var data_total_findings = api_data.total_findings
var chart_data_total_findings = [
  {
    x: data_total_findings.map((object) => object.year),
    y: data_total_findings.map((object) => object.total),
    text: data_total_findings.map((object) =>
      new Intl.NumberFormat('en-US', { maximumSignificantDigits: 6 }).format(
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
]
var chart_layout_total_findings = {
  title: {
    text: 'Total Findings',
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Count',
    },
  },
}

Plotly.newPlot(
  'div_total_findings',
  chart_data_total_findings,
  chart_layout_total_findings,
  config
)

/**
 * PERCENT SUBMISSIONS WITH FINDINGS
 * Bar chart, one bar per year
 */
var data_submissions_with_findings = api_data.submissions_with_findings
var chart_data_submissions_with_findings = [
  {
    x: data_submissions_with_findings.map((object) => object.year),
    y: data_submissions_with_findings.map((object) => object.total),
    text: data_submissions_with_findings.map((object) =>
      new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3 }).format(
        object.total
      ) + '%'
    ),
    textposition: 'outside',
    marker: {
      color: '#56B833', // FAC logo green
      width: 1,
    },
    type: 'bar',
  },
]
var chart_layout_submissions_with_findings = {
  title: {
    text: '% Submissions with Findings',
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Percentage',
    },
  },
}

Plotly.newPlot(
  'div_total_submissions_with_findings',
  chart_data_submissions_with_findings,
  chart_layout_submissions_with_findings,
  config
)


/**
 * AUDITEE RISK PROFILE
 * Pie charts, one chart per year
 */
var data_auditee_risk_profile = api_data.auditee_risk_profile
var chart_data_auditee_risk_profile = []
data_auditee_risk_profile.forEach(
  (object, index) => chart_data_auditee_risk_profile.push({
      labels: ["Low Risk", "Not Low Risk"],
      values: [object.low_risk, object.not_low_risk],
      name: object.year,
      hoverinfo: 'label+percent',
      type: 'pie',
      domain: {
        row: Math.floor(index / 2),
        column: index % 2
      },
      // automargin: true
  })
)
var chart_layout_auditee_risk_profile = {
  title: {
    text: `Auditee Risk Profile`,
  },
  annotations: [],  // Populated dynamically below
  // 'autosize' doesn't seem to work with subplots.
  height: 450 + (150 * (data_auditee_risk_profile.length - 2)),
  width: 850,
  autosize: true,
  grid: {rows: Math.ceil(data_auditee_risk_profile.length / 2), columns: 2},
  showlegend: true,
}
// Note: The pie charts should all become their own charts, not subplots, in order to title them properly.
// This is a strange solution to annotate each chart with the appropriate title.
data_auditee_risk_profile.forEach(
  (object, index) => chart_layout_auditee_risk_profile.annotations.push({
      text: object.year,
      showarrow: false,
      x: index % 2 ? 0.77 : 0.24,
      xref: "paper",
      xanchor: "center",
      y: 1.006 - ((Math.floor(index / 2)) / (Math.ceil(data_auditee_risk_profile.length / 2))),
      yref: "paper",
      yanchor: Math.floor(index / 2) ? "top" : "bottom",
  })
)

Plotly.newPlot(
  'div_auditee_risk_profile',
  chart_data_auditee_risk_profile,
  chart_layout_auditee_risk_profile,
  config
)


/**
 * PERCENT RISK PROFILE VS PERCENT FINDINGS
 * Grouped bar chart, % not low risk vs % submissions with findings
 */
var data_risk_profile_vs_findings = api_data.risk_profile_vs_findings
var chart_data_risk_profile_vs_findings = [
  // Trace one, % not low risk
  {
    x: data_risk_profile_vs_findings.map((object) => object.year),
    y: data_risk_profile_vs_findings.map((object) => object.not_low_risk),
    text: data_risk_profile_vs_findings.map((object) =>
      new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3 }).format(
        object.not_low_risk
      ) + '%'
    ),
    textposition: 'outside',
    marker: {
      color: '#56B833', // FAC logo green
      width: 1,
    },
    name: '% Not Low-Risk Auditees',
    type: 'bar',
  },
  // Trace two, % submissions with findings
  {
    x: data_risk_profile_vs_findings.map((object) => object.year),
    y: data_risk_profile_vs_findings.map((object) => object.audits_with_findings),
    text: data_risk_profile_vs_findings.map((object) =>
      new Intl.NumberFormat('en-US', { maximumSignificantDigits: 3 }).format(
        object.audits_with_findings
      ) + '%'
    ),
    textposition: 'outside',
    marker: {
      color: '#152973', // FAC logo dark blue
      width: 1,
    },
    name: '% Submissions With Findings',
    type: 'bar',
  }
]
var chart_layout_risk_profile_vs_findings = {
  title: {
    text: '% Not Low-Risk vs % With Findings by Year',
  },
  xaxis: {
    title: {
      text: 'Year',
    },
    type: 'category',
  },
  yaxis: {
    title: {
      text: 'Percentage',
    },
    ticksuffix: "%"
  },
}

Plotly.newPlot(
  'div_risk_profile_vs_findings',
  chart_data_risk_profile_vs_findings,
  chart_layout_risk_profile_vs_findings,
  config
)
