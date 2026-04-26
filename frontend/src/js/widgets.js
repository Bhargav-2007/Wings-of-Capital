// Chart.js widget rendering for Wings of Capital
window.WOC_Charts = {
  renderBalanceChart: function(ctx, timeseries) {
    return new Chart(ctx, {
      type: 'line',
      data: {
        labels: timeseries.map(d => d.date),
        datasets: [{
          label: 'Balance',
          data: timeseries.map(d => d.value),
          fill: true,
          backgroundColor: function(context) {
            const chart = context.chart;
            const {ctx, chartArea} = chart;
            if (!chartArea) return 'rgba(99,102,241,0.2)';
            const gradient = ctx.createLinearGradient(0, 0, 0, chartArea.bottom);
            gradient.addColorStop(0, 'rgba(99,102,241,0.3)');
            gradient.addColorStop(1, 'rgba(99,102,241,0)');
            return gradient;
          },
          borderColor: '#6366f1',
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: '#6366f1',
          pointHoverRadius: 6,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#e0e7ef22' }, beginAtZero: false }
        }
      }
    });
  },
  renderEarningsChart: function(ctx, percent) {
    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Current', 'Goal'],
        datasets: [{
          data: [percent, 100 - percent],
          backgroundColor: ['#6366f1', '#e5e7eb'],
          borderWidth: 0,
          borderRadius: 10,
          cutout: '80%',
        }]
      },
      options: {
        cutout: '80%',
        plugins: { legend: { display: false } },
      }
    });
  },
  renderSpendingChart: function(ctx, cats) {
    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels: Object.keys(cats),
        datasets: [{
          label: 'Spending',
          data: Object.values(cats),
          backgroundColor: ['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe'],
          borderRadius: { topLeft: 8, topRight: 8 },
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#e0e7ef22' }, beginAtZero: true }
        }
      }
    });
  }
};
