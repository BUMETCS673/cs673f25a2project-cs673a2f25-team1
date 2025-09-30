import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'http://127.0.0.1:5000';

// Add token to all requests
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle unauthorized responses
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('token');
      window.location.href = '/'; // Will be handled by React router in production
    }
    return Promise.reject(error);
  }
);
