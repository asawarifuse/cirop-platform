import axios from 'axios';

const API_URL = 'http://localhost:3001/api/v1';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const customerAPI = {
  getAll: (params) => api.get('/customers', { params }),
  getById: (id) => api.get(`/customers/${id}`),
};

export const orderAPI = {
  getRevenue: () => api.get('/orders/analytics/revenue'),
  getProducts: () => api.get('/orders/analytics/products'),
  getFrequency: () => api.get('/orders/analytics/frequency'),
  getAOV: () => api.get('/orders/analytics/aov'),
};

export default api;