// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital - Vanilla SPA Router & Application
 * Client-side routing with history API
 */

class Router {
    constructor() {
        this.routes = {};
        this.currentRoute = null;
        this.setupHistoryListener();
    }
    
    /**
     * Register a route
     */
    register(path, component, requiresAuth = false) {
        this.routes[path] = { component, requiresAuth };
    }
    
    /**
     * Setup history API listener
     */
    setupHistoryListener() {
        window.addEventListener('hashchange', () => this.navigate());
        window.addEventListener('DOMContentLoaded', () => this.navigate());
    }
    
    /**
     * Navigate to a route
     */
    async navigate(path = null) {
        // Get path from URL hash if not provided
        if (!path) {
            path = window.location.hash.slice(1) || '/login';
        }
        
        // Check authentication
        if (this.routes[path]?.requiresAuth && !AuthManager.isAuthenticated()) {
            window.location.hash = '#/login';
            return;
        }
        
        // Get route component
        const route = this.routes[path] || this.routes['/404'];
        if (!route) {
            console.error(`Route not found: ${path}`);
            return;
        }
        
        try {
            // Clear loading state
            const loadingEl = document.getElementById('app-loading');
            const contentEl = document.getElementById('app-content');
            
            if (loadingEl && contentEl) {
                loadingEl.classList.add('hidden');
                contentEl.classList.remove('hidden');
            }
            
            // Render component
            const viewContainer = document.getElementById('view-container');
            if (viewContainer) {
                await route.component(viewContainer);
            }
            
            this.currentRoute = path;
            window.scrollTo(0, 0);
        } catch (error) {
            console.error(`Error rendering route ${path}:`, error);
            stateManager.addNotification(error.message, 'danger');
        }
    }
}

// Create global router instance
const router = new Router();

// Register routes
router.register('/login', async (container) => {
    await renderLogin(container);
});

router.register('/dashboard', async (container) => {
    await renderDashboard(container);
}, true);

router.register('/portfolio', async (container) => {
    await renderPortfolio(container);
}, true);

router.register('/trading', async (container) => {
    await renderTrading(container);
}, true);

router.register('/analytics', async (container) => {
    await renderAnalytics(container);
}, true);

function renderToasts(notifications) {
    const container = document.getElementById('toast-container');
    if (!container) {
        return;
    }

    const colorMap = {
        success: 'bg-green-600',
        danger: 'bg-red-600',
        warning: 'bg-amber-500',
        info: 'bg-blue-600',
    };

    container.innerHTML = notifications
        .map((toast) => {
            const color = colorMap[toast.type] || colorMap.info;
            return `
                <div class="${color} text-white px-4 py-3 rounded-lg shadow-lg">
                    ${toast.message}
                </div>
            `;
        })
        .join('');
}

// Initialize app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    // Subscribe to state changes
    stateManager.subscribe((state) => {
        // Update nav visibility based on auth
        const navHeader = document.querySelector('nav');
        if (navHeader) {
            navHeader.style.display = state.isAuthenticated ? 'block' : 'none';
        }
        
        // Update logout button if authenticated
        if (state.isAuthenticated) {
            const logoutBtn = document.getElementById('logout-btn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', async () => {
                    await AuthManager.logout();
                    window.location.hash = '#/login';
                });
            }
        }

        renderToasts(state.notifications);
    });
    
    // Setup theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => stateManager.toggleTheme());
    }
    
    // Navigate to initial route
    router.navigate();
});
