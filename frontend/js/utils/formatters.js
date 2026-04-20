// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

const Formatters = {
    currency(value, currency = 'USD') {
        const number = Number(value);
        if (Number.isNaN(number)) {
            return '$0.00';
        }
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency,
            maximumFractionDigits: 2,
        }).format(number);
    },
    percent(value) {
        const number = Number(value);
        if (Number.isNaN(number)) {
            return '0.00%';
        }
        return `${number.toFixed(2)}%`;
    },
    number(value, digits = 2) {
        const number = Number(value);
        if (Number.isNaN(number)) {
            return '0';
        }
        return number.toFixed(digits);
    },
    date(value) {
        try {
            return new Date(value).toLocaleDateString();
        } catch {
            return '';
        }
    },
};
