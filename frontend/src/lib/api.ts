/**
 * API Client for ChainIntel Backend
 */
import axios, { AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      timeout: 60000, // 60 seconds for ML model training
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // DIMO Endpoints
  async getNetworkMetrics() {
    const response = await this.client.get('/api/dimo/metrics');
    return response.data;
  }

  async getHistoricalData(days: number = 90) {
    const response = await this.client.get(`/api/dimo/historical?days=${days}`);
    return response.data;
  }

  async checkHealth() {
    const response = await this.client.get('/api/dimo/health');
    return response.data;
  }

  // Analytics Endpoints
  async generateForecast(daysAhead: number = 180) {
    const response = await this.client.post(`/api/analytics/forecast?days_ahead=${daysAhead}`);
    return response.data;
  }

  async getLatestForecast() {
    const response = await this.client.get('/api/analytics/forecast/latest');
    return response.data;
  }

  async getGrowthRate() {
    const response = await this.client.get('/api/analytics/growth-rate');
    return response.data;
  }

  async getAnalyticsSummary() {
    const response = await this.client.get('/api/analytics/summary');
    return response.data;
  }
}

export const apiClient = new APIClient();
