// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital - Client-side State Management
 * Simple flux-like state management for vanilla JS
 */

class StateManager {
    constructor() {
        this.state = {
            user: null,
            isAuthenticated: false,
            tokens: {
                accessToken: null,
                refreshToken: null,
            },
            theme: localStorage.getItem('theme') || 'dark',
            notifications: [],
            loading: false,
            error: null,
        };
        
        this.listeners = [];
    }
    
    /**
     * Subscribe to state changes
     */
    subscribe(callback) {
        this.listeners.push(callback);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }
    
    /**
     * Notify all listeners of state changes
     */
    notify() {
        this.listeners.forEach(callback => callback(this.state));
    }
    
    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    }
    
    /**
     * Update state
     */
    setState(updates) {
        this.state = {
            ...this.state,
            ...updates,
        };
        this.notify();
    }
    
    /**
     * Set user and authentication
     */
    setUser(user, accessToken, refreshToken) {
        this.setState({
            user,
            isAuthenticated: !!user,
            tokens: {
                accessToken,
                refreshToken,
            },
        });
        
        // Persist auth data to localStorage
        if (user) {
            localStorage.setItem('user', JSON.stringify(user));
            localStorage.setItem('accessToken', accessToken);
            localStorage.setItem('refreshToken', refreshToken);
        } else {
            localStorage.removeItem('user');
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
        }
    }
    
    /**
     * Clear user and authentication
     */
    clearUser() {
        this.setUser(null, null, null);
    }
    
    /**
     * Add notification
     */
    addNotification(message, type = 'info', duration = 3000) {
        const notification = {
            id: Date.now(),
            message,
            type,
        };
        
        this.state.notifications.push(notification);
        this.notify();
        
        // Auto-remove after duration
        setTimeout(() => {
            this.removeNotification(notification.id);
        }, duration);
    }
    
    /**
     * Remove notification
     */
    removeNotification(id) {
        this.state.notifications = this.state.notifications.filter(n => n.id !== id);
        this.notify();
    }
    
    /**
     * Set loading state
     */
    setLoading(loading) {
        this.setState({ loading });
    }
    
    /**
     * Set error
     */
    setError(error) {
        this.setState({ error });
    }
    
    /**
     * Toggle theme
     */
    toggleTheme() {
        const newTheme = this.state.theme === 'dark' ? 'light' : 'dark';
        this.setState({ theme: newTheme });
        localStorage.setItem('theme', newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
    }
    
    /**
     * Restore state from localStorage
     */
    restoreFromStorage() {
        const user = localStorage.getItem('user');
        const accessToken = localStorage.getItem('accessToken');
        const refreshToken = localStorage.getItem('refreshToken');
        const theme = localStorage.getItem('theme') || 'dark';
        
        if (user && accessToken) {
            this.setState({
                user: JSON.parse(user),
                isAuthenticated: true,
                tokens: { accessToken, refreshToken },
                theme,
            });
        }
    }
}

// Create global state manager instance
const stateManager = new StateManager();

// Restore state on page load
window.addEventListener('DOMContentLoaded', () => {
    stateManager.restoreFromStorage();
    document.documentElement.setAttribute('data-theme', stateManager.state.theme);
});
