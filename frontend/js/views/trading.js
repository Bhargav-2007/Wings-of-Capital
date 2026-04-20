// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

async function renderTrading(container) {
    container.innerHTML = `
        <div class="space-y-6">
            <header class="flex items-center justify-between">
                <div>
                    <h2 class="text-2xl font-semibold">Trading Desk</h2>
                    <p class="text-gray-400">Live price feed for tracked symbols.</p>
                </div>
                <button id="refresh-prices" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg">Refresh</button>
            </header>
            <div id="price-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"></div>
        </div>
    `;

    const grid = container.querySelector('#price-grid');

    async function loadPrices() {
        if (!grid) {
            return;
        }
        try {
            const response = await apiClient.get('/crypto/prices?symbols=BTC,ETH,SOL,USDT');
            grid.innerHTML = response.data
                .map(
                    (quote) => `
                    <div class="bg-gray-800 border border-gray-700 rounded-xl p-4 shadow">
                        <p class="text-sm text-gray-400">${quote.symbol}</p>
                        <p class="text-xl font-semibold">${Formatters.currency(quote.price)}</p>
                        <p class="text-xs text-gray-500">Updated ${Formatters.date(quote.last_updated)}</p>
                    </div>
                `
                )
                .join('');
        } catch (error) {
            grid.innerHTML = '<p class="text-gray-400">Unable to load prices.</p>';
        }
    }

    const refreshBtn = container.querySelector('#refresh-prices');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadPrices);
    }

    await loadPrices();
}
