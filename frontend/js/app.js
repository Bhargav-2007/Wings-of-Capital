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
                viewContainer.innerHTML = '';
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
    container.innerHTML = await renderLogin();
});

router.register('/dashboard', async (container) => {
    container.innerHTML = await renderDashboard();
}, true);

router.register('/portfolio', async (container) => {
    container.innerHTML = await renderPortfolio();
}, true);

router.register('/trading', async (container) => {
    container.innerHTML = await renderTrading();
}, true);

router.register('/analytics', async (container) => {
    container.innerHTML = await renderAnalytics();
}, true);

// Stub render functions (will be implemented in respective view files)
async function renderLogin() {
    return '<div>Login view - placeholder</div>';
}

async function renderDashboard() {
    return '<div>Dashboard view - placeholder</div>';
}

async function renderPortfolio() {
    return '<div>Portfolio view - placeholder</div>';
}

async function renderTrading() {
    return '<div>Trading view - placeholder</div>';
}

async function renderAnalytics() {
    return '<div>Analytics view - placeholder</div>';
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
    });
    
    // Setup theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => stateManager.toggleTheme());
    }
    
    // Navigate to initial route
    router.navigate();
});
