import React, { createContext, useState, useContext, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { authAPI } from '../services/api';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();

    // Set up periodic auth check (every 5 minutes)
    // This will catch expired tokens and automatically logout
    const authCheckInterval = setInterval(() => {
      if (user) {
        checkAuth();
      }
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(authCheckInterval);
  }, [user]);

  const checkAuth = async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (token) {
        const userData = await authAPI.getMe();
        setUser(userData);
      } else {
        // No token found, ensure user is null
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // If 401, token is invalid/expired - already cleared by interceptor
      if (error.response?.status === 401) {
        setUser(null);
      } else {
        // For other errors, also clear token to be safe
        await AsyncStorage.removeItem('token');
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      await authAPI.login(email, password);
      const userData = await authAPI.getMe();
      setUser(userData);
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);

      // If 401, token was already cleared by interceptor
      if (error.response?.status === 401) {
        setUser(null);
      }

      // Provide detailed error messages
      let errorMessage = 'Login failed';

      if (error.message === 'Network Error' || error.code === 'ECONNREFUSED') {
        errorMessage = 'Cannot connect to server. Please check:\n• Server URL is correct\n• Server is running\n• You are on the same network';
      } else if (error.response) {
        // Server responded with error
        if (error.response.status === 401) {
          errorMessage = 'Incorrect email or password';
        } else if (error.response.status === 404) {
          errorMessage = 'Server endpoint not found. Check your server URL ends with /api';
        } else if (error.response.status >= 500) {
          errorMessage = 'Server error. Please try again later';
        } else {
          errorMessage = error.response?.data?.detail || `Error: ${error.response.status}`;
        }
      } else if (error.request) {
        // Request made but no response
        errorMessage = 'No response from server. Please check:\n• Server is running\n• Network connection\n• Firewall settings';
      }

      return {
        success: false,
        error: errorMessage,
      };
    }
  };

  const register = async (email, password) => {
    try {
      await authAPI.register(email, password);
      // Auto-login after registration
      return await login(email, password);
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      };
    }
  };

  const logout = async () => {
    await authAPI.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

