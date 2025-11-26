/**
 * Axios instance configuration - Firebase Authentication
 */
import axios from 'axios';
import { auth } from '../config/firebase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add Firebase ID token
api.interceptors.request.use(
  async (config) => {
    const user = auth.currentUser;
    if (user) {
      try {
        // Get fresh Firebase ID token
        const token = await user.getIdToken();
        config.headers.Authorization = `Bearer ${token}`;
      } catch (error) {
        console.error('Error getting Firebase token:', error);
        // Try to use cached token from localStorage
        const cachedToken = localStorage.getItem('firebaseToken');
        if (cachedToken) {
          config.headers.Authorization = `Bearer ${cachedToken}`;
        }
      }
    } else {
      // No Firebase user, try cached token
      const cachedToken = localStorage.getItem('firebaseToken');
      if (cachedToken) {
        config.headers.Authorization = `Bearer ${cachedToken}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const user = auth.currentUser;
        
        if (!user) {
          // No Firebase user, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }

        // Force refresh Firebase token
        const newToken = await user.getIdToken(true);
        localStorage.setItem('firebaseToken', newToken);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, clear tokens and redirect to login
        localStorage.removeItem('firebaseToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
