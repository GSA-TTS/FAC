import Plotly from 'plotly.js-dist';

var api_data = JSON.parse(document.getElementById('dashboard_data').textContent);

var config = {responsive: true}

var pie_chart_data = [
  {
    labels: api_data['labels'],
    values: api_data['values'],
    hoverinfo: 'label+percent',
    hole: 0.4,
    type: 'pie',
  }
];

var pie_chart_layout = {
  title: {
    text: 'Funding By Entity Type',
  },
  height: 400,
  width: 600,
  showlegend: true,
  grid: { rows: 1, columns: 1}
};


Plotly.newPlot('dashboard_piechart_div', pie_chart_data, pie_chart_layout, config);


var bar_chart_data = [
  {
    x: api_data['values'],
    y: api_data['labels'],
    orientation: 'h',
    name: 'Dollars (Billions)',
    marker: {
      // color: '#152973',  // FAC logo dark blue
      color: '#56B833',  // FAC logo green
      width: 1
    },
    type: 'bar'
  }
]

var bar_chart_layout = {
  title: {
    text: 'Funding By Entity Type',
  },
  height: 400,
  width: 600,
  showlegend: true,
  grid: { rows: 1, columns: 1}
};

Plotly.newPlot('dashboard_barchart_div', bar_chart_data, bar_chart_layout, config);
