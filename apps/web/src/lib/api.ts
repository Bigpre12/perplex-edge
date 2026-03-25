import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://perplex-edge-backend-production.up.railway.app';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Helper for error handling
export const handleApiError = (error: any) => {
  console.error('API Error:', error.response?.data || error.message);
  return error.response?.data || { detail: 'An unexpected error occurred' };
};
