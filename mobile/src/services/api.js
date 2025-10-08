import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE_URL } from '../config';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: async (email, password) => {
    const response = await api.post('/auth/register', { email, password });
    return response.data;
  },
  
  login: async (email, password) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    if (response.data.access_token) {
      await AsyncStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },
  
  logout: async () => {
    await AsyncStorage.removeItem('token');
  },
  
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Books API
export const booksAPI = {
  searchBooks: async (query, maxResults = 10) => {
    const response = await api.get('/books/search/', {
      params: { q: query, max_results: maxResults },
    });
    return response.data;
  },

  getBooks: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.reading_status) {
      params.append('reading_status', filters.reading_status);
    }
    if (filters.is_wishlist !== undefined) {
      params.append('is_wishlist', filters.is_wishlist);
    }

    const queryString = params.toString();
    const response = await api.get(`/books/${queryString ? '?' + queryString : ''}`);
    return response.data;
  },

  getBook: async (bookId) => {
    const response = await api.get(`/books/${bookId}/`);
    return response.data;
  },

  addBookByISBN: async (isbn, reading_status = 'want_to_read', is_wishlist = false) => {
    const response = await api.post('/books/isbn/', {
      isbn,
      reading_status,
      is_wishlist,
    });
    return response.data;
  },

  addBookManually: async (bookData) => {
    const response = await api.post('/books/', bookData);
    return response.data;
  },

  updateBook: async (bookId, updates) => {
    const response = await api.patch(`/books/${bookId}/`, updates);
    return response.data;
  },

  deleteBook: async (bookId) => {
    await api.delete(`/books/${bookId}/`);
  },

  getCollections: async () => {
    const response = await api.get('/books/collections/');
    return response.data;
  },

  getMissingBooks: async (seriesName) => {
    const response = await api.get(`/books/collections/${encodeURIComponent(seriesName)}/missing`);
    return response.data;
  },
};

export default api;

