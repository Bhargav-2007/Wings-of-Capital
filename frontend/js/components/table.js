// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

const TableRenderer = {
    render(headers, rows) {
        const headerHtml = headers.map((header) => `<th class="px-4 py-2 text-left text-sm text-gray-300">${header}</th>`).join('');
        const rowsHtml = rows
            .map(
                (row) =>
                    `<tr class="border-t border-gray-700">${row
                        .map((cell) => `<td class="px-4 py-2 text-sm">${cell}</td>`)
                        .join('')}</tr>`
            )
            .join('');

        return `
            <div class="overflow-x-auto">
                <table class="min-w-full text-left">
                    <thead>
                        <tr>${headerHtml}</tr>
                    </thead>
                    <tbody>${rowsHtml}</tbody>
                </table>
            </div>
        `;
    },
};
