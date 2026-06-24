const axios = require('axios');

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';

const mlApiService = {
  async getCustomerPrediction(customerId) {
    try {
      const response = await axios.get(`${ML_API_URL}/predictions/customer/${customerId}`);
      return response.data;
    } catch (error) {
      console.error(`ML API error for customer ${customerId}:`, error.message);
      return null;
    }
  },

  async getSegments() {
    try {
      const response = await axios.get(`${ML_API_URL}/predictions/segments`);
      return response.data;
    } catch (error) {
      console.error('ML API segments error:', error.message);
      return [];
    }
  },

  async getForecast() {
    try {
      const response = await axios.get(`${ML_API_URL}/predictions/forecast`);
      return response.data;
    } catch (error) {
      console.error('ML API forecast error:', error.message);
      return null;
    }
  },

  async getChurnSummary() {
    try {
      const response = await axios.get(`${ML_API_URL}/predictions/churn`);
      return response.data;
    } catch (error) {
      console.error('ML API churn error:', error.message);
      return [];
    }
  },

  async getScenarios() {
    try {
      const response = await axios.get(`${ML_API_URL}/scenarios`);
      return response.data;
    } catch (error) {
      console.error('ML API scenarios error:', error.message);
      return null;
    }
  },
};

module.exports = mlApiService;