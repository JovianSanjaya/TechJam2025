// API Configuration
export const API_CONFIG = {
  // Get API URL from environment variable or fallback to default
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // API endpoints
  ENDPOINTS: {
    ANALYZE: '/analyze',
    HEALTH: '/health',
    SAMPLE: '/analyze/sample'
  }
}

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`
}


