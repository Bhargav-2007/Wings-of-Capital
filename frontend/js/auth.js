// Copyright 2026 Bhargav (Wings of Capital). All Rights Reserved.
// Licensed under the Apache License, Version 2.0.

/**
 * Wings of Capital - Authentication Management
 * Handles login, logout, token refresh, and MFA
 */

class AuthManager {
    /**
     * Login with email and password
     */
    static async login(email, password) {
        try {
            stateManager.setLoading(true);
            const response = await apiClient.post('/auth/login', { email, password });
            
            stateManager.setUser(
                response.user,
                response.access_token,
                response.refresh_token
            );
            
            stateManager.addNotification('Logged in successfully', 'success');
            return response.user;
        } catch (error) {
            stateManager.addNotification(error.message, 'danger');
            throw error;
        } finally {
            stateManager.setLoading(false);
        }
    }
    
    /**
     * Logout
     */
    static async logout() {
        try {
            stateManager.setLoading(true);
            await apiClient.post('/auth/logout', {});
            stateManager.clearUser();
            stateManager.addNotification('Logged out successfully', 'success');
        } catch (error) {
            stateManager.addNotification(error.message, 'danger');
        } finally {
            stateManager.setLoading(false);
        }
    }
    
    /**
     * Register new user
     */
    static async register(email, password, passwordConfirm) {
        try {
            stateManager.setLoading(true);
            
            if (password !== passwordConfirm) {
                throw new Error('Passwords do not match');
            }
            
            const response = await apiClient.post('/auth/register', {
                email,
                password,
            });
            
            stateManager.addNotification('Registration successful. Please check your email to verify.', 'success');
            return response;
        } catch (error) {
            stateManager.addNotification(error.message, 'danger');
            throw error;
        } finally {
            stateManager.setLoading(false);
        }
    }
    
    /**
     * Refresh access token
     */
    static async refreshToken() {
        try {
            const state = stateManager.getState();
            const refreshToken = state.tokens?.refreshToken;
            
            if (!refreshToken) {
                throw new Error('No refresh token available');
            }
            
            const response = await apiClient.post('/auth/refresh', {
                refresh_token: refreshToken,
            });
            
            stateManager.setState({
                tokens: {
                    accessToken: response.access_token,
                    refreshToken: response.refresh_token,
                },
            });
            
            return response;
        } catch (error) {
            stateManager.clearUser();
            throw error;
        }
    }
    
    /**
     * Get current user profile
     */
    static async getMe() {
        try {
            return await apiClient.get('/auth/me');
        } catch (error) {
            console.error('Failed to fetch user profile:', error);
            throw error;
        }
    }

    /**
     * Use a pre-generated access token for development
     */
    static useToken(accessToken, userId = 'dev-user', email = 'dev@local') {
        if (!accessToken) {
            throw new Error('Access token is required');
        }

        const user = {
            id: userId,
            email,
        };

        stateManager.setUser(user, accessToken, null);
        stateManager.addNotification('Token stored for this session', 'success');
        return user;
    }
    
    /**
     * Enable MFA
     */
    static async enableMFA() {
        try {
            stateManager.setLoading(true);
            return await apiClient.post('/auth/mfa/enable', {});
        } finally {
            stateManager.setLoading(false);
        }
    }
    
    /**
     * Verify MFA code
     */
    static async verifyMFA(code) {
        try {
            stateManager.setLoading(true);
            return await apiClient.post('/auth/mfa/verify', { code });
        } finally {
            stateManager.setLoading(false);
        }
    }
    
    /**
     * Check if user is authenticated
     */
    static isAuthenticated() {
        const state = stateManager.getState();
        return state.isAuthenticated && !!state.tokens?.accessToken;
    }
}
