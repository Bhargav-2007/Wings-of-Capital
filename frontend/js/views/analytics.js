// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

async function renderAnalytics(container) {
    container.innerHTML = `
        <div class="space-y-8">
            <section class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-semibold">Portfolio Analytics</h2>
                        <p class="text-gray-400">PnL trends and allocation insights.</p>
                    </div>
                    <button id="analytics-refresh" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg">
                        Refresh
                    </button>
                </div>
                <div id="analytics-summary" class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6"></div>
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
                        <h3 class="text-lg font-semibold mb-2">PnL History</h3>
                        <div class="h-64"><canvas id="pnl-chart"></canvas></div>
                    </div>
                    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
                        <h3 class="text-lg font-semibold mb-2">Allocation</h3>
                        <div class="h-64"><canvas id="allocation-chart"></canvas></div>
                    </div>
                </div>
            </section>

            <section class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                <h2 class="text-2xl font-semibold">AI Model Registry</h2>
                <p class="text-gray-400 mb-4">Latest deployed and archived models.</p>
                <div id="model-table"></div>
            </section>
        </div>
    `;

    const summaryContainer = container.querySelector('#analytics-summary');
    const modelTable = container.querySelector('#model-table');
    const pnlCanvas = container.querySelector('#pnl-chart');
    const allocationCanvas = container.querySelector('#allocation-chart');
    let pnlChart = null;
    let allocationChart = null;

    async function loadAnalytics() {
        try {
            const [summary, history, allocation, models] = await Promise.all([
                apiClient.get('/crypto/reports/pnl-summary'),
                apiClient.get('/crypto/reports/pnl-history?days=30'),
                apiClient.get('/crypto/reports/allocation-history?days=30'),
                apiClient.get('/crypto/ai/models'),
            ]);

            if (summaryContainer) {
                summaryContainer.innerHTML = `
                    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
                        <p class="text-gray-400 text-sm">Total Value</p>
                        <p class="text-xl font-semibold">${Formatters.currency(summary.total_value)}</p>
                    </div>
                    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
                        <p class="text-gray-400 text-sm">Total PnL</p>
                        <p class="text-xl font-semibold">${Formatters.currency(summary.total_pnl)}</p>
                    </div>
                    <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
                        <p class="text-gray-400 text-sm">PnL %</p>
                        <p class="text-xl font-semibold">${Formatters.percent(summary.pnl_percent)}</p>
                    </div>
                `;
            }

            const historyLabels = history.points.map((point) => point.date);
            const historyValues = history.points.map((point) => Number(point.total_value));

            if (pnlCanvas) {
                ChartHelpers.destroyChart(pnlChart);
                pnlChart = ChartComponents.createLineChart(
                    pnlCanvas,
                    historyLabels,
                    historyValues,
                    'Total Value',
                    '#38bdf8'
                );
            }

            if (allocationCanvas) {
                const lastPoint = allocation.points[allocation.points.length - 1];
                if (lastPoint) {
                    const labels = Object.keys(lastPoint.allocation);
                    const values = labels.map((key) => Number(lastPoint.allocation[key]));
                    const colors = labels.map((_, index) => {
                        const palette = ['#22c55e', '#3b82f6', '#f97316', '#a855f7', '#0ea5e9'];
                        return palette[index % palette.length];
                    });

                    ChartHelpers.destroyChart(allocationChart);
                    allocationChart = ChartComponents.createDoughnutChart(
                        allocationCanvas,
                        labels,
                        values,
                        colors
                    );
                }
            }

            if (modelTable) {
                if (!models || models.length === 0) {
                    modelTable.innerHTML = '<p class="text-gray-400">No models found.</p>';
                } else {
                    const rows = models.map((model) => [
                        model.model_name,
                        model.version,
                        model.status,
                        Formatters.number(model.accuracy, 4),
                        Formatters.date(model.deployment_date),
                    ]);
                    modelTable.innerHTML = TableRenderer.render(
                        ['Model', 'Version', 'Status', 'Accuracy', 'Deployed'],
                        rows
                    );
                }
            }
        } catch (error) {
            if (summaryContainer) {
                summaryContainer.innerHTML = '<p class="text-gray-400">Sign in to view analytics.</p>';
            }
            if (modelTable) {
                modelTable.innerHTML = '<p class="text-gray-400">Model registry unavailable.</p>';
            }
        }
    }

    const refreshBtn = container.querySelector('#analytics-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadAnalytics);
    }

    await loadAnalytics();
}
