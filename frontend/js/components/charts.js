// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital — Chart.js Component Wrappers
 *
 * All chart types used in the dashboard:
 *  - LineChart:   Bezier curve with linear gradient fill (Balance)
 *  - DonutChart:  80% cutout, round line caps (Earnings)
 *  - BarChart:    Vertical bars with top border-radius (Spending)
 *
 * Each wrapper:
 *  - Destroys existing instance before re-render (prevents canvas memory leak)
 *  - Reads CSS Custom Properties for colors (theme-aware)
 *  - Returns the Chart.js instance for external control
 */

'use strict';

// ── Chart registry (track instances to destroy on re-render) ────
const _chartRegistry = new Map();

function destroyIfExists(canvasId) {
  const existing = _chartRegistry.get(canvasId);
  if (existing) { existing.destroy(); _chartRegistry.delete(canvasId); }
}

function registerChart(canvasId, instance) {
  _chartRegistry.set(canvasId, instance);
  return instance;
}

// ── CSS custom property helper ───────────────────────────────────
function cssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// ── Gradient factory for canvas ──────────────────────────────────
function makeGradient(ctx, height, colorStart, colorEnd = 'rgba(0,0,0,0)') {
  const grad = ctx.createLinearGradient(0, 0, 0, height);
  grad.addColorStop(0, colorStart);
  grad.addColorStop(1, colorEnd);
  return grad;
}

// ── Base Chart.js defaults (applied once) ────────────────────────
function applyGlobalDefaults() {
  if (!window.Chart) return;
  Chart.defaults.font.family      = cssVar('--font-sans') || 'Inter, sans-serif';
  Chart.defaults.font.size        = 12;
  Chart.defaults.color            = cssVar('--color-text-tertiary') || '#888';
  Chart.defaults.plugins.legend.display = false;
  Chart.defaults.plugins.tooltip.backgroundColor = cssVar('--color-surface-1') || '#1e2030';
  Chart.defaults.plugins.tooltip.titleColor       = cssVar('--color-text-primary') || '#fff';
  Chart.defaults.plugins.tooltip.bodyColor        = cssVar('--color-text-secondary') || '#aaa';
  Chart.defaults.plugins.tooltip.borderColor      = cssVar('--color-border') || '#333';
  Chart.defaults.plugins.tooltip.borderWidth      = 1;
  Chart.defaults.plugins.tooltip.padding          = 12;
  Chart.defaults.plugins.tooltip.cornerRadius     = 10;
  Chart.defaults.plugins.tooltip.displayColors    = false;
}

// ──────────────────────────────────────────────────────────────────
// LINE CHART — Balance Overview
// Bezier curve (tension 0.4) + linear gradient fill
// ──────────────────────────────────────────────────────────────────
function LineChart(canvasId, labels, datasets, options = {}) {
  if (!window.Chart) { console.error('[Charts] Chart.js not loaded'); return null; }
  applyGlobalDefaults();
  destroyIfExists(canvasId);

  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const ctx = canvas.getContext('2d');

  // Build gradient fills per dataset
  const processedDatasets = datasets.map((ds, i) => {
    const colors = [
      cssVar('--chart-1'),
      cssVar('--chart-2'),
      cssVar('--chart-3'),
      cssVar('--chart-4'),
    ];
    const baseColor = ds.color || colors[i % colors.length];
    const grad = makeGradient(
      ctx,
      canvas.offsetHeight || 200,
      baseColor.replace('hsl', 'hsla').replace(')', ', 0.35)'),
      baseColor.replace('hsl', 'hsla').replace(')', ', 0)')
    );

    return {
      label:           ds.label || '',
      data:            ds.data  || [],
      borderColor:     baseColor,
      backgroundColor: grad,
      borderWidth:     2.5,
      tension:         0.4,    // Bezier per spec
      fill:            true,
      pointRadius:     3,
      pointHoverRadius:6,
      pointBackgroundColor: baseColor,
      pointBorderColor:     'transparent',
      ...ds.extra,
    };
  });

  const chart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets: processedDatasets },
    options: {
      responsive:         true,
      maintainAspectRatio:false,
      interaction:        { mode: 'index', intersect: false },
      plugins: {
        legend: { display: datasets.length > 1 },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.formattedValue}`,
          },
        },
      },
      scales: {
        x: {
          grid:  { display: false },
          border:{ display: false },
          ticks: { color: cssVar('--color-text-tertiary'), maxTicksLimit: 7 },
        },
        y: {
          grid:  { color: cssVar('--color-border-subtle'), drawBorder: false },
          border:{ display: false, dash: [4, 4] },
          ticks: {
            color:    cssVar('--color-text-tertiary'),
            callback: v => options.yFormatter ? options.yFormatter(v) : v,
          },
          beginAtZero: options.beginAtZero ?? false,
        },
      },
      animation: { duration: 600, easing: 'easeInOutQuart' },
      ...options.extra,
    },
  });

  return registerChart(canvasId, chart);
}

// ──────────────────────────────────────────────────────────────────
// DONUT CHART — Earnings
// 80% cutout, round caps
// ──────────────────────────────────────────────────────────────────
function DonutChart(canvasId, labels, data, options = {}) {
  if (!window.Chart) return null;
  applyGlobalDefaults();
  destroyIfExists(canvasId);

  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const ctx = canvas.getContext('2d');

  const defaultColors = [
    cssVar('--chart-1'), cssVar('--chart-2'), cssVar('--chart-3'),
    cssVar('--chart-4'), cssVar('--chart-5'), cssVar('--chart-6'),
  ];

  const chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor:      options.colors || defaultColors,
        borderColor:          cssVar('--color-surface-1'),
        borderWidth:          3,
        hoverBorderWidth:     4,
        hoverOffset:          8,
        borderRadius:         6,    // round caps per spec
        spacing:              2,
      }],
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      cutout:              '80%',   // per spec
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.label}: ${options.formatter
              ? options.formatter(ctx.raw)
              : ctx.formattedValue
            }`,
          },
        },
      },
      animation: { duration: 800, easing: 'easeInOutQuart', animateRotate: true },
    },
  });

  return registerChart(canvasId, chart);
}

// ──────────────────────────────────────────────────────────────────
// BAR CHART — Spending
// Vertical bars with top border-radius
// ──────────────────────────────────────────────────────────────────
function BarChart(canvasId, labels, datasets, options = {}) {
  if (!window.Chart) return null;
  applyGlobalDefaults();
  destroyIfExists(canvasId);

  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const ctx = canvas.getContext('2d');

  const colors = [
    cssVar('--chart-1'), cssVar('--chart-2'), cssVar('--chart-3'),
    cssVar('--chart-4'), cssVar('--chart-5'),
  ];

  const processedDatasets = datasets.map((ds, i) => ({
    label:           ds.label || '',
    data:            ds.data  || [],
    backgroundColor: ds.color || colors[i % colors.length],
    borderRadius:    { topLeft: 6, topRight: 6 },   // top border-radius per spec
    borderSkipped:   false,
    hoverBackgroundColor: (ds.color || colors[i % colors.length])
      .replace('hsl', 'hsla').replace(')', ', 0.8)') || ds.color,
    maxBarThickness: 40,
    ...ds.extra,
  }));

  const chart = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets: processedDatasets },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      interaction:         { mode: 'index', intersect: false },
      plugins: {
        legend: { display: datasets.length > 1 },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${
              options.yFormatter ? options.yFormatter(ctx.raw) : ctx.formattedValue
            }`,
          },
        },
      },
      scales: {
        x: {
          grid:  { display: false },
          border:{ display: false },
          ticks: { color: cssVar('--color-text-tertiary') },
          stacked: options.stacked || false,
        },
        y: {
          grid:  { color: cssVar('--color-border-subtle') },
          border:{ display: false },
          ticks: {
            color:    cssVar('--color-text-tertiary'),
            callback: v => options.yFormatter ? options.yFormatter(v) : v,
          },
          beginAtZero: true,
          stacked: options.stacked || false,
        },
      },
      animation: { duration: 600, easing: 'easeInOutQuart' },
      ...options.extra,
    },
  });

  return registerChart(canvasId, chart);
}

// ──────────────────────────────────────────────────────────────────
// AREA CHART (alias for LineChart with fill=true, for portfolio)
// ──────────────────────────────────────────────────────────────────
const AreaChart = LineChart;

// ──────────────────────────────────────────────────────────────────
// Update chart data without full re-render
// ──────────────────────────────────────────────────────────────────
function updateChartData(canvasId, labels, newData, datasetIndex = 0) {
  const chart = _chartRegistry.get(canvasId);
  if (!chart) return;
  chart.data.labels = labels;
  chart.data.datasets[datasetIndex].data = newData;
  chart.update('active');
}

// ── Re-apply defaults when theme changes ─────────────────────────
document.addEventListener('woc:themechange', () => {
  _chartRegistry.forEach(chart => {
    applyGlobalDefaults();
    chart.update('none');
  });
});
