/**
 * API Service
 * Handles all communication with the backend API
 */

import axios from 'axios';

// Base URL for API requests
// Change this to your production API URL when deploying
const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add authentication token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ===== AUTH API =====

export const authAPI = {
  // Register a new user
  register: (username, email, password) =>
    api.post('/api/auth/register', { username, email, password }),
  
  // Login with username and password
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // Get current user information
  getCurrentUser: () => api.get('/api/auth/me'),
};

// ===== CONTENT API =====

export const contentAPI = {
  // Get all content with optional filters
  getAll: (params = {}) => api.get('/api/content/', { params }),
  
  // Get single content by ID
  getById: (id) => api.get(`/api/content/${id}`),
  
  // Get content by slug
  getBySlug: (slug) => api.get(`/api/content/slug/${slug}`),
  
  // Create new content
  create: (data) => api.post('/api/content/', data),
  
  // Update existing content
  update: (id, data) => api.put(`/api/content/${id}`, data),
  
  // Delete content
  delete: (id) => api.delete(`/api/content/${id}`),
};

// ===== CATEGORY API =====

export const categoryAPI = {
  // Get all categories
  getAll: () => api.get('/api/categories/'),
  
  // Get single category by ID
  getById: (id) => api.get(`/api/categories/${id}`),
  
  // Create new category
  create: (data) => api.post('/api/categories/', data),
  
  // Update existing category
  update: (id, data) => api.put(`/api/categories/${id}`, data),
  
  // Delete category
  delete: (id) => api.delete(`/api/categories/${id}`),
};

export default api;

