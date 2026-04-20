// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

async function renderDashboard(container) {
    container.innerHTML = `
        <div class="space-y-8">
            <section class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                <div class="flex items-center justify-between">
                    <div>
                        <h2 class="text-2xl font-semibold">System Status</h2>
                        <p class="text-gray-400">Live health checks across services.</p>
                    </div>
                    <button id="refresh-status" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg">
                        Refresh
                    </button>
                </div>
                <div id="status-grid" class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6"></div>
            </section>

            <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                    <h3 class="text-xl font-semibold mb-4">Portfolio Snapshot</h3>
                    <div id="portfolio-summary" class="space-y-3"></div>
                </div>
                <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                    <h3 class="text-xl font-semibold mb-4">Quick Actions</h3>
                    <div class="space-y-3">
                        <button id="action-refresh-prices" class="w-full bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-lg">
                            Refresh Prices
                        </button>
                        <button id="action-evaluate-alerts" class="w-full bg-emerald-600 hover:bg-emerald-700 px-4 py-2 rounded-lg">
                            Evaluate Alerts
                        </button>
                        <button id="action-train-model" class="w-full bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg">
                            Train Baseline Model
                        </button>
                    </div>
                </div>
            </section>
        </div>
    `;

    const statusGrid = container.querySelector('#status-grid');
    const portfolioSummary = container.querySelector('#portfolio-summary');

    const renderStatus = (label, ok, details) => {
        const statusColor = ok ? 'text-emerald-400' : 'text-amber-400';
        const statusLabel = ok ? 'Healthy' : 'Degraded';
        return `
            <div class="bg-gray-900 border border-gray-700 rounded-lg p-4">
                <p class="text-sm text-gray-400">${label}</p>
                <p class="text-lg font-semibold ${statusColor}">${statusLabel}</p>
                <p class="text-xs text-gray-500 mt-2">${details}</p>
            </div>
        `;
    };

    async function loadStatus() {
        const endpoints = [
            { label: 'Auth Service', endpoint: '/auth/health' },
            { label: 'Ledger Service', endpoint: '/ledger/health' },
            { label: 'Crypto Service', endpoint: '/crypto/health' },
        ];

        const results = await Promise.allSettled(
            endpoints.map((item) => apiClient.get(item.endpoint))
        );

        if (statusGrid) {
            statusGrid.innerHTML = results
                .map((result, index) => {
                    const label = endpoints[index].label;
                    if (result.status === 'fulfilled') {
                        const deps = result.value.dependencies || {};
                        const ok = Object.values(deps).every(Boolean);
                        const details = Object.entries(deps)
                            .map(([key, value]) => `${key}: ${value ? 'ok' : 'fail'}`)
                            .join(' | ');
                        return renderStatus(label, ok, details || 'No dependency data');
                    }
                    return renderStatus(label, false, 'Unavailable');
                })
                .join('');
        }
    }

    async function loadPortfolioSummary() {
        if (!portfolioSummary) {
            return;
        }

        try {
            const summary = await apiClient.get('/crypto/reports/pnl-summary');
            portfolioSummary.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="text-gray-400">Total Value</span>
                    <span class="font-semibold">${Formatters.currency(summary.total_value)}</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-gray-400">Total PnL</span>
                    <span class="font-semibold">${Formatters.currency(summary.total_pnl)}</span>
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-gray-400">PnL %</span>
                    <span class="font-semibold">${Formatters.percent(summary.pnl_percent)}</span>
                </div>
            `;
        } catch (error) {
            portfolioSummary.innerHTML = `
                <p class="text-gray-400">Sign in to view your portfolio summary.</p>
            `;
        }
    }

    const refreshBtn = container.querySelector('#refresh-status');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadStatus();
            loadPortfolioSummary();
        });
    }

    const refreshPricesBtn = container.querySelector('#action-refresh-prices');
    if (refreshPricesBtn) {
        refreshPricesBtn.addEventListener('click', async () => {
            await apiClient.post('/crypto/tasks/refresh-prices', {});
            stateManager.addNotification('Price refresh task queued', 'success');
        });
    }

    const evaluateAlertsBtn = container.querySelector('#action-evaluate-alerts');
    if (evaluateAlertsBtn) {
        evaluateAlertsBtn.addEventListener('click', async () => {
            await apiClient.post('/crypto/tasks/evaluate-alerts', {});
            stateManager.addNotification('Alert evaluation task queued', 'success');
        });
    }

    const trainModelBtn = container.querySelector('#action-train-model');
    if (trainModelBtn) {
        trainModelBtn.addEventListener('click', async () => {
            await apiClient.post('/crypto/tasks/train-model', {});
            stateManager.addNotification('Training task queued', 'success');
        });
    }

    await loadStatus();
    await loadPortfolioSummary();
}
