import Chart from 'chart.js/auto'

const data = JSON.parse(document.getElementById('dashboard_data').textContent);

(async function() {
  new Chart(
    document.getElementById('dashboard_sample'),
    {
      type: 'doughnut',
      data: {
        labels: data.map(row => row.entity_type),
        datasets: [
          {
            label: "Funding by Entity Type",
            data: data.map(row => row.sum)
          }
        ]
      }
    }
  );
})();
