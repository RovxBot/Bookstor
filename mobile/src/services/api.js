import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Get server URL from AsyncStorage
const getServerUrl = async () => {
  const serverUrl = await AsyncStorage.getItem('serverUrl');
  if (!serverUrl) {
    throw new Error('Server URL not configured. Please set it in the login screen.');
  }
  return serverUrl;
};

// Create axios instance without baseURL (will be set per request)
const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token and server URL to requests
api.interceptors.request.use(
  async (config) => {
    // Get server URL from AsyncStorage
    const serverUrl = await getServerUrl();
    config.baseURL = serverUrl;

    // Add auth token if available
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

// Handle 401 errors (unauthorized) - automatically logout
api.interceptors.response.use(
  (response) => {
    // Pass through successful responses
    return response;
  },
  async (error) => {
    // Check if error is 401 Unauthorized
    if (error.response && error.response.status === 401) {
      // Clear token from storage
      await AsyncStorage.removeItem('token');

      // Note: We can't directly navigate here as we don't have access to navigation
      // The AuthContext will detect the missing token and redirect to login
      // This is handled by the checkAuth function in AuthContext

      console.log('401 Unauthorized - Token cleared, user will be logged out');
    }

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
    const serverUrl = await getServerUrl();
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axios.post(`${serverUrl}/auth/login`, formData, {
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

  setServerUrl: async (url) => {
    // Ensure URL doesn't end with slash
    const cleanUrl = url.trim().replace(/\/$/, '');
    await AsyncStorage.setItem('serverUrl', cleanUrl);
  },

  getServerUrl: async () => {
    return await AsyncStorage.getItem('serverUrl');
  },

  getRegistrationStatus: async () => {
    const serverUrl = await getServerUrl();
    const response = await axios.get(`${serverUrl}/auth/registration-status`);
    return response.data;
  },

  toggleRegistration: async (enabled) => {
    const response = await api.post('/auth/toggle-registration', null, {
      params: { enabled }
    });
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

