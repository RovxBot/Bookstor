import React, { createContext, useContext, useState, useEffect } from 'react';
import { useColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const ThemeContext = createContext();

const lightTheme = {
  mode: 'light',
  colors: {
    background: '#f5f5f5',
    surface: '#ffffff',
    primary: '#007AFF',
    secondary: '#5856D6',
    text: '#000000',
    textSecondary: '#666666',
    border: '#e0e0e0',
    error: '#d32f2f',
    success: '#4caf50',
    card: '#ffffff',
    notification: '#ff3b30',
    inactive: '#f0f0f0',
    placeholder: '#999999',
  },
};

const darkTheme = {
  mode: 'dark',
  colors: {
    background: '#000000',
    surface: '#1c1c1e',
    primary: '#0a84ff',
    secondary: '#5e5ce6',
    text: '#ffffff',
    textSecondary: '#98989d',
    border: '#38383a',
    error: '#ff453a',
    success: '#32d74b',
    card: '#2c2c2e',
    notification: '#ff453a',
    inactive: '#3a3a3c',
    placeholder: '#636366',
  },
};

export function ThemeProvider({ children }) {
  const systemColorScheme = useColorScheme();
  const [themeMode, setThemeMode] = useState('system'); // 'light', 'dark', 'system'
  const [currentTheme, setCurrentTheme] = useState(
    systemColorScheme === 'dark' ? darkTheme : lightTheme
  );

  // Load saved theme preference on mount
  useEffect(() => {
    loadThemePreference();
  }, []);

  // Update theme when system theme or theme mode changes
  useEffect(() => {
    if (themeMode === 'system') {
      setCurrentTheme(systemColorScheme === 'dark' ? darkTheme : lightTheme);
    } else if (themeMode === 'dark') {
      setCurrentTheme(darkTheme);
    } else {
      setCurrentTheme(lightTheme);
    }
  }, [themeMode, systemColorScheme]);

  const loadThemePreference = async () => {
    try {
      const savedTheme = await AsyncStorage.getItem('themeMode');
      if (savedTheme) {
        setThemeMode(savedTheme);
      }
    } catch (error) {
      console.error('Error loading theme preference:', error);
    }
  };

  const changeTheme = async (newThemeMode) => {
    try {
      await AsyncStorage.setItem('themeMode', newThemeMode);
      setThemeMode(newThemeMode);
    } catch (error) {
      console.error('Error saving theme preference:', error);
    }
  };

  return (
    <ThemeContext.Provider
      value={{
        theme: currentTheme,
        themeMode,
        changeTheme,
        isDark: currentTheme.mode === 'dark',
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

