import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/');

// Tasks
export const getTasks = (params = {}) => api.get('/tasks/', { params });
export const getTodayTasks = () => api.get('/tasks/today/');
export const getTask = (id) => api.get(`/tasks/${id}/`);
export const createTask = (data) => api.post('/tasks/', data);
export const updateTask = (id, data) => api.patch(`/tasks/${id}/`, data);
export const completeTask = (id, data) => api.post(`/tasks/${id}/complete/`, data);
export const assignTask = (id, staffId) => api.post(`/tasks/${id}/assign/`, { staff_id: staffId });

// Customers
export const getCustomers = (params = {}) => api.get('/customers/', { params });
export const getCustomer = (id) => api.get(`/customers/${id}/`);
export const getAtRiskCustomers = () => api.get('/customers/at_risk/');
export const getVipCustomers = () => api.get('/customers/vip/');

// Products
export const getProducts = (params = {}) => api.get('/products/', { params });
export const getProduct = (id) => api.get(`/products/${id}/`);

// Brands
export const getBrands = (params = {}) => api.get('/brands/', { params });
export const getBrand = (id) => api.get(`/brands/${id}/`);

// Staff
export const getStaff = () => api.get('/staff/');
export const getLeaderboard = (period = 'weekly') => api.get('/staff/leaderboard/', { params: { period } });

// Excel Upload
export const uploadExcel = (file, fileType) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('file_type', fileType);
  return api.post('/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
export const getUploadHistory = () => api.get('/uploads/');

// Actions
export const generateTasks = () => api.post('/generate-tasks/');
export const updateSegments = () => api.post('/update-segments/');

export default api;
