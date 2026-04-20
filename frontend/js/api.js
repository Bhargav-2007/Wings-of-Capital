// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital - API Client with Fetch Wrapper
 * Handles authentication, error handling, and request/response intercepting
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL || `http://localhost:8000/api/v1`;
        this.timeout = 30000;
    }
    
    /**
     * Get authorization token from state
     */
    getAuthToken() {
        const state = stateManager.getState();
        return state.tokens?.accessToken;
    }
    
    /**
     * Build request options with auth and headers
     */
    buildRequestOptions(options = {}) {
        const token = this.getAuthToken();
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return {
            ...options,
            headers,
        };
    }
    
    /**
     * Make HTTP request with retry and error handling
     */
    async request(endpoint, options = {}, retries = 3, allowRefresh = true) {
        const url = `${this.baseURL}${endpoint}`;
        const requestOptions = this.buildRequestOptions(options);
        
        try {
            // Apply timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                ...requestOptions,
                signal: controller.signal,
            });
            
            clearTimeout(timeoutId);
            
            // Handle 401 Unauthorized (token expired)
            if (response.status === 401) {
                const state = stateManager.getState();
                if (allowRefresh && state.tokens?.refreshToken) {
                    try {
                        await AuthManager.refreshToken();
                        return this.request(endpoint, options, retries, false);
                    } catch (refreshError) {
                        stateManager.clearUser();
                        window.location.href = '/#/login';
                        throw refreshError;
                    }
                }

                stateManager.clearUser();
                window.location.href = '/#/login';
                throw new Error('Session expired. Please login again.');
            }
            
            // Parse response
            let data;
            try {
                data = await response.json();
            } catch {
                data = null;
            }
            
            // Handle errors
            if (!response.ok) {
                const error = new Error(data?.detail || data?.message || 'Request failed');
                error.status = response.status;
                error.data = data;
                throw error;
            }
            
            return data;
        } catch (error) {
            // Retry on network errors (not on 4xx/5xx)
            if (retries > 0 && !error.status) {
                console.warn(`Retrying request to ${endpoint}... (${3 - retries + 1}/3)`);
                await new Promise(resolve => setTimeout(resolve, 1000));
                return this.request(endpoint, options, retries - 1);
            }
            
            throw error;
        }
    }
    
    /**
     * GET request
     */
    get(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'GET' });
    }
    
    /**
     * POST request
     */
    post(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: JSON.stringify(data),
        });
    }
    
    /**
     * PUT request
     */
    put(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }
    
    /**
     * DELETE request
     */
    delete(endpoint, options = {}) {
        return this.request(endpoint, { ...options, method: 'DELETE' });
    }
    
    /**
     * Patch request
     */
    patch(endpoint, data, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }
}

// Create global API client instance
const apiClient = new APIClient();
