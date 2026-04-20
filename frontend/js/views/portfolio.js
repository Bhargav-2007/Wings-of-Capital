// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

async function renderPortfolio(container) {
    container.innerHTML = `
        <div class="space-y-6">
            <header class="flex items-center justify-between">
                <div>
                    <h2 class="text-2xl font-semibold">Portfolio</h2>
                    <p class="text-gray-400">Current holdings and performance.</p>
                </div>
                <button id="portfolio-refresh" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg">
                    Refresh
                </button>
            </header>
            <div id="portfolio-table" class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow"></div>
        </div>
    `;

    const tableContainer = container.querySelector('#portfolio-table');

    async function loadPortfolio() {
        if (!tableContainer) {
            return;
        }
        try {
            const data = await apiClient.get('/crypto/portfolio');
            if (!data.holdings || data.holdings.length === 0) {
                tableContainer.innerHTML = '<p class="text-gray-400">No holdings found.</p>';
                return;
            }

            const rows = data.holdings.map((holding) => [
                holding.symbol,
                Formatters.number(holding.quantity, 4),
                Formatters.currency(holding.current_price),
                Formatters.currency(holding.current_value),
                Formatters.currency(holding.pnl),
                Formatters.percent(holding.pnl_percent),
            ]);

            tableContainer.innerHTML = TableRenderer.render(
                ['Symbol', 'Quantity', 'Price', 'Value', 'PnL', 'PnL %'],
                rows
            );
        } catch (error) {
            tableContainer.innerHTML = '<p class="text-gray-400">Sign in to view holdings.</p>';
        }
    }

    const refreshBtn = container.querySelector('#portfolio-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadPortfolio);
    }

    await loadPortfolio();
}
