import axios from 'axios';

const API_BASE_URL = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const facilityService = {
  // Get all facilities
  async getFacilities(type = null, includeClosed = false) {
    const params = {};
    if (type) params.facility_type = type;
    if (includeClosed) params.include_closed = true;

    const response = await apiClient.get('/facilities', { params });
    return response.data;
  },

  // Get specific facility details
  async getFacility(id) {
    const response = await apiClient.get(`/facilities/${id}`);
    return response.data;
  },

  // Get facility estimate
  async getEstimate(id) {
    const response = await apiClient.get(`/facilities/${id}/estimate`);
    return response.data;
  },
};

export const reportService = {
  // Submit a student report
  async submitReport(reportData) {
    const response = await apiClient.post('/reports', reportData);
    return response.data;
  },

  // Get recent reports
  async getReports(facilityId = null, hours = 24) {
    const params = { hours };
    if (facilityId) params.facility_id = facilityId;

    const response = await apiClient.get('/reports', { params });
    return response.data;
  },
};

export const recommendationService = {
  // Get AI recommendations
  async getRecommendations(query, options = {}) {
    const response = await apiClient.post('/recommend', {
      query,
      ...options,
    });
    return response.data;
  },

  // Plan a route across facilities
  async planRoute(query, options = {}) {
    const response = await apiClient.post('/plan', {
      query,
      ...options,
    });
    return response.data;
  },
};

export default apiClient;
