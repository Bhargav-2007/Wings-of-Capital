// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

async function renderLogin(container) {
    container.innerHTML = `
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                <h2 class="text-2xl font-semibold mb-4">Welcome back</h2>
                <p class="text-gray-400 mb-6">Sign in with your account credentials.</p>

                <form id="login-form" class="space-y-4">
                    <div>
                        <label class="block text-sm text-gray-300 mb-1">Email</label>
                        <input
                            id="login-email"
                            type="email"
                            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2"
                            placeholder="you@example.com"
                            required
                        />
                    </div>
                    <div>
                        <label class="block text-sm text-gray-300 mb-1">Password</label>
                        <input
                            id="login-password"
                            type="password"
                            class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2"
                            placeholder="Enter your password"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        class="w-full bg-blue-600 hover:bg-blue-700 rounded-lg px-4 py-2"
                    >
                        Login
                    </button>
                </form>
            </div>

            <div class="space-y-6">
                <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                    <h2 class="text-2xl font-semibold mb-4">Create an account</h2>
                    <form id="register-form" class="space-y-4">
                        <div>
                            <label class="block text-sm text-gray-300 mb-1">Email</label>
                            <input
                                id="register-email"
                                type="email"
                                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2"
                                placeholder="you@example.com"
                                required
                            />
                        </div>
                        <div>
                            <label class="block text-sm text-gray-300 mb-1">Password</label>
                            <input
                                id="register-password"
                                type="password"
                                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2"
                                placeholder="At least 12 characters"
                                required
                            />
                        </div>
                        <div>
                            <label class="block text-sm text-gray-300 mb-1">Confirm Password</label>
                            <input
                                id="register-password-confirm"
                                type="password"
                                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2"
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            class="w-full bg-emerald-600 hover:bg-emerald-700 rounded-lg px-4 py-2"
                        >
                            Register
                        </button>
                    </form>
                </div>

                <div class="bg-gray-800 border border-gray-700 rounded-xl p-6 shadow">
                    <h2 class="text-2xl font-semibold mb-4">Use a dev token</h2>
                    <p class="text-gray-400 mb-4">Paste a generated access token to skip email verification.</p>
                    <form id="token-form" class="space-y-4">
                        <div>
                            <label class="block text-sm text-gray-300 mb-1">User ID (optional)</label>
                            <input
                                id="token-user-id"
                                type="text"
                                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2"
                                placeholder="UUID used in the token"
                            />
                        </div>
                        <div>
                            <label class="block text-sm text-gray-300 mb-1">Email (optional)</label>
                            <input
                                id="token-email"
                                type="email"
                                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2"
                                placeholder="dev@example.com"
                            />
                        </div>
                        <div>
                            <label class="block text-sm text-gray-300 mb-1">Access Token</label>
                            <textarea
                                id="token-value"
                                class="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 h-28"
                                placeholder="Paste the JWT access token here"
                                required
                            ></textarea>
                        </div>
                        <button
                            type="submit"
                            class="w-full bg-purple-600 hover:bg-purple-700 rounded-lg px-4 py-2"
                        >
                            Use Token
                        </button>
                    </form>
                </div>
            </div>
        </div>
    `;

    const loginForm = container.querySelector('#login-form');
    const registerForm = container.querySelector('#register-form');
    const tokenForm = container.querySelector('#token-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = container.querySelector('#login-email').value.trim();
            const password = container.querySelector('#login-password').value;
            await AuthManager.login(email, password);
            window.location.hash = '#/dashboard';
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const email = container.querySelector('#register-email').value.trim();
            const password = container.querySelector('#register-password').value;
            const passwordConfirm = container.querySelector('#register-password-confirm').value;
            await AuthManager.register(email, password, passwordConfirm);
        });
    }

    if (tokenForm) {
        tokenForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const token = container.querySelector('#token-value').value.trim();
            const userId = container.querySelector('#token-user-id').value.trim();
            const email = container.querySelector('#token-email').value.trim();
            AuthManager.useToken(token, userId || 'dev-user', email || 'dev@local');
            window.location.hash = '#/dashboard';
        });
    }
}
