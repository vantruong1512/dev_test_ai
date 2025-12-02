import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000, // Increased to 60 seconds for LLM responses
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error?.response?.data?.detail || 
                        error?.response?.data?.message || 
                        error?.response?.data?.error ||
                        error.message || 
                        'Lỗi kết nối server';
    return Promise.reject(new Error(errorMessage));
  }
);

export default apiClient;
