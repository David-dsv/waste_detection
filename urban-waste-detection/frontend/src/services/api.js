/**
 * Service API pour communication avec le backend Flask.
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Detection
export const detectImage = async (formData) => {
  const response = await api.post('/detect', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const detectVideo = async (formData) => {
  const response = await api.post('/detect/video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDetections = async (params = {}) => {
  const response = await api.get('/detections', { params });
  return response.data;
};

export const getDetection = async (id) => {
  const response = await api.get(`/detections/${id}`);
  return response.data;
};

export const deleteDetection = async (id) => {
  const response = await api.delete(`/detections/${id}`);
  return response.data;
};

// API Alerts
export const getAlerts = async (params = {}) => {
  const response = await api.get('/alerts', { params });
  return response.data;
};

export const resolveAlert = async (id) => {
  const response = await api.post(`/alerts/${id}/resolve`);
  return response.data;
};

// API Statistics
export const getOverviewStats = async () => {
  const response = await api.get('/statistics/overview');
  return response.data;
};

export const getDailyStats = async () => {
  const response = await api.get('/statistics/daily');
  return response.data;
};

export const getClassDistribution = async () => {
  const response = await api.get('/statistics/by-class');
  return response.data;
};

export default api;
