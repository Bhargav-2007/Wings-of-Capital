// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

const FormHelpers = {
    getInputValue(form, selector) {
        const element = form.querySelector(selector);
        return element ? element.value.trim() : '';
    },
};
