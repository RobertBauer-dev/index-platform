import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      baseURL: config.baseURL,
      fullURL: `${config.baseURL}${config.url}`,
      headers: config.headers,
      data: config.data
    });
    
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 Added auth token to request');
    }
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', {
      status: response.status,
      statusText: response.statusText,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      url: error.config?.url,
      data: error.response?.data,
      message: error.message
    });
    
    if (error.response?.status === 401) {
      console.log('🔒 401 Unauthorized - redirecting to login');
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Auth
  auth: {
    login: (username: string, password: string) =>
      apiClient.post('/auth/token', new URLSearchParams({ username, password, grant_type: 'password' }), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      }),
    me: () => apiClient.get('/auth/me'),
    register: (userData: any) => apiClient.post('/auth/register', userData),
  },

  // Securities
  securities: {
    list: (params?: any) => apiClient.get('/securities', { params }),
    get: (id: number) => apiClient.get(`/securities/${id}`),
    getBySymbol: (symbol: string) => apiClient.get(`/securities/symbol/${symbol}`),
    create: (data: any) => apiClient.post('/securities', data),
    update: (id: number, data: any) => apiClient.put(`/securities/${id}`, data),
    delete: (id: number) => apiClient.delete(`/securities/${id}`),
    getPrices: (id: number, params?: any) => apiClient.get(`/securities/${id}/prices`, { params }),
    getSectors: () => apiClient.get('/securities/sectors'),
    getCountries: () => apiClient.get('/securities/countries'),
    // Market Cap endpoints
    updateMarketCap: (id: number, source?: string) => apiClient.post(`/securities/${id}/market-cap/update`, null, { 
      params: { source: source || 'auto' } 
    }),
    batchUpdateMarketCap: (symbols: string[], source?: string) => apiClient.post('/securities/market-cap/batch-update', null, {
      params: { 
        symbols: symbols,
        source: source || 'auto'
      }
    }),
    updateAllMarketCaps: (source?: string, limit?: number) => apiClient.post('/securities/market-cap/update-all', null, {
      params: { 
        source: source || 'auto',
        limit: limit || 100
      }
    }),
  },

  // Indices
  indices: {
    list: (params?: any) => apiClient.get('/indices', { params }),
    get: (id: number) => apiClient.get(`/indices/${id}`),
    create: (data: any) => apiClient.post('/indices', data),
    update: (id: number, data: any) => apiClient.put(`/indices/${id}`, data),
    delete: (id: number) => apiClient.delete(`/indices/${id}`),
    getValues: (id: number, params?: any) => apiClient.get(`/indices/${id}/values`, { params }),
    getConstituents: (id: number, params?: any) => apiClient.get(`/indices/${id}/constituents`, { params }),
    calculate: (id: number, date?: string) => apiClient.post(`/indices/${id}/calculate`, null, { params: { date } }),
    rebalance: (id: number, date?: string) => apiClient.post(`/indices/${id}/rebalance`, null, { params: { date } }),
    backtest: (id: number, startDate: string, endDate?: string, frequency?: string) =>
      apiClient.post(`/indices/${id}/backtest`, null, {
        params: { start_date: startDate, end_date: endDate, rebalance_frequency: frequency }
      }),
    getPerformance: (id: number) => apiClient.get(`/indices/${id}/performance`),
    createCustom: (data: any) => apiClient.post('/indices/custom-index', data),
  },

  // Price Data
  prices: {
    list: (params?: any) => apiClient.get('/prices', { params }),
    get: (id: number) => apiClient.get(`/prices/${id}`),
    create: (data: any) => apiClient.post('/prices', data),
    createBulk: (data: any[]) => apiClient.post('/prices/bulk', data),
    update: (id: number, data: any) => apiClient.put(`/prices/${id}`, data),
    delete: (id: number) => apiClient.delete(`/prices/${id}`),
    getLatest: (symbol: string) => apiClient.get(`/prices/latest/${symbol}`),
    getHistory: (symbol: string, params?: any) => apiClient.get(`/prices/symbol/${symbol}/history`, { params }),
    getLatestMultiple: (symbols: string[]) => apiClient.get('/prices/symbols/latest', { params: { symbols } }),
  },

  // Data Ingestion
  ingestion: {
    csvSecurities: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/ingestion/csv/securities', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    csvPrices: (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/ingestion/csv/prices', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
    alphaVantage: (symbols: string[]) => apiClient.post('/ingestion/api/alpha-vantage', symbols),
    yahooFinance: (symbols: string[], startDate?: string, endDate?: string) =>
      apiClient.post('/ingestion/api/yahoo-finance', symbols, {
        params: { start_date: startDate, end_date: endDate }
      }),
    securitiesFromAPI: (symbols: string[]) => apiClient.post('/ingestion/api/securities', symbols),
    getTemplate: (dataType: string) => apiClient.get(`/ingestion/templates/${dataType}`),
    bulkIngest: (files: { securities?: File; prices: File[] }) => {
      const formData = new FormData();
      if (files.securities) {
        formData.append('securities_file', files.securities);
      }
      files.prices.forEach(file => {
        formData.append('prices_files', file);
      });
      return apiClient.post('/ingestion/bulk', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
    },
  },
};
