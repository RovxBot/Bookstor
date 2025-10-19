import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { authAPI } from '../services/api';

export default function LoginScreen({ navigation }) {
  const [serverUrl, setServerUrl] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [registrationEnabled, setRegistrationEnabled] = useState(false);
  const [checkingRegistration, setCheckingRegistration] = useState(false);
  const { login } = useAuth();
  const { theme } = useTheme();

  const styles = createStyles(theme);

  // Load saved server URL on mount
  useEffect(() => {
    const loadServerUrl = async () => {
      const savedUrl = await authAPI.getServerUrl();
      if (savedUrl) {
        setServerUrl(savedUrl);
        checkRegistrationStatus(savedUrl);
      }
    };
    loadServerUrl();
  }, []);

  // Check registration status when server URL changes
  const checkRegistrationStatus = async (url) => {
    if (!url) return;

    setCheckingRegistration(true);
    try {
      await authAPI.setServerUrl(url);
      const status = await authAPI.getRegistrationStatus();
      setRegistrationEnabled(status.enabled);
    } catch (error) {
      console.log('Could not check registration status:', error);
      setRegistrationEnabled(false);
    } finally {
      setCheckingRegistration(false);
    }
  };

  const testConnection = async () => {
    if (!serverUrl) {
      Alert.alert('Error', 'Please enter a server URL');
      return;
    }

    // Validate server URL format
    if (!serverUrl.startsWith('http://') && !serverUrl.startsWith('https://')) {
      Alert.alert('Error', 'Server URL must start with http:// or https://');
      return;
    }

    setTestingConnection(true);

    try {
      await authAPI.setServerUrl(serverUrl);

      // Extract base URL (remove /api if present)
      const baseUrl = serverUrl.replace(/\/api\/?$/, '');

      // Try to fetch the health endpoint
      const axios = require('axios');
      const response = await axios.get(`${baseUrl}/health`, {
        timeout: 5000,
      });

      if (response.status === 200) {
        Alert.alert(
          'Connection Successful! ✅',
          `Server is reachable and responding.\n\nYou can now log in with your credentials.`,
          [{ text: 'OK' }]
        );
        // Also check registration status after successful connection
        checkRegistrationStatus(serverUrl);
      }
    } catch (error) {
      console.error('Connection test error:', error);

      let errorMessage = 'Connection failed';

      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        errorMessage = 'Connection timeout. Server is not responding.\n\nCheck:\n• Server is running\n• URL is correct\n• Port number is included';
      } else if (error.code === 'ECONNREFUSED') {
        errorMessage = 'Connection refused.\n\nCheck:\n• Server is running\n• Firewall is not blocking the connection';
      } else if (error.message === 'Network Error') {
        errorMessage = 'Network error.\n\nCheck:\n• You are on the same network as the server\n• Server IP address is correct\n• WiFi is connected';
      } else {
        errorMessage = `Connection failed: ${error.message}`;
      }

      Alert.alert('Connection Test Failed ❌', errorMessage);
    } finally {
      setTestingConnection(false);
    }
  };

  const handleLogin = async () => {
    if (!serverUrl || !email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    // Validate server URL format
    if (!serverUrl.startsWith('http://') && !serverUrl.startsWith('https://')) {
      Alert.alert('Error', 'Server URL must start with http:// or https://');
      return;
    }

    setLoading(true);

    // Save server URL
    await authAPI.setServerUrl(serverUrl);

    const result = await login(email, password);
    setLoading(false);

    if (!result.success) {
      Alert.alert('Login Failed', result.error);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'bottom']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
      >
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.content}>
            <Text style={styles.title}>📚 Bookstor</Text>
            <Text style={styles.subtitle}>Your Personal Library</Text>

          <Text style={styles.label}>Server URL</Text>
          <TextInput
            style={styles.input}
            placeholder="http://192.168.1.100:8000/api"
            placeholderTextColor={theme.colors.textSecondary}
            value={serverUrl}
            onChangeText={(text) => {
              setServerUrl(text);
              if (text.startsWith('http://') || text.startsWith('https://')) {
                checkRegistrationStatus(text);
              }
            }}
            onBlur={() => {
              if (serverUrl.startsWith('http://') || serverUrl.startsWith('https://')) {
                checkRegistrationStatus(serverUrl);
              }
            }}
            autoCapitalize="none"
            keyboardType="url"
          />
          <Text style={styles.hint}>
            Enter the URL of your Bookstor server (e.g., http://192.168.1.100:8000/api)
          </Text>

          <TouchableOpacity
            style={styles.testButton}
            onPress={testConnection}
            disabled={testingConnection || !serverUrl}
          >
            {testingConnection ? (
              <ActivityIndicator color={theme.colors.primary} />
            ) : (
              <Text style={styles.testButtonText}>Test Connection</Text>
            )}
          </TouchableOpacity>

          <Text style={styles.label}>Email</Text>
          <TextInput
            style={styles.input}
            placeholder="Email"
            placeholderTextColor={theme.colors.textSecondary}
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />

          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="Password"
            placeholderTextColor={theme.colors.textSecondary}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <TouchableOpacity
            style={styles.button}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Login</Text>
            )}
          </TouchableOpacity>

          {registrationEnabled && (
            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => navigation.navigate('Register')}
            >
              <Text style={styles.linkText}>
                Don't have an account? Register
              </Text>
            </TouchableOpacity>
          )}

          {!registrationEnabled && !checkingRegistration && serverUrl && (
            <Text style={styles.disabledText}>
              Registration is currently disabled
            </Text>
          )}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const createStyles = (theme) => StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  scrollContent: {
    flexGrow: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 56,
    fontWeight: '700',
    textAlign: 'center',
    marginBottom: 8,
    color: theme.colors.text,
    letterSpacing: -1,
  },
  subtitle: {
    fontSize: 20,
    textAlign: 'center',
    color: theme.colors.textSecondary,
    marginBottom: 48,
    fontWeight: '400',
    letterSpacing: 0.3,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: 8,
    marginTop: 8,
  },
  input: {
    backgroundColor: theme.colors.card,
    padding: 15,
    borderRadius: 10,
    marginBottom: 8,
    fontSize: 16,
    borderWidth: 1,
    borderColor: theme.colors.border,
    color: theme.colors.text,
  },
  hint: {
    fontSize: 12,
    color: theme.colors.textSecondary,
    marginBottom: 8,
    fontStyle: 'italic',
  },
  testButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: theme.colors.primary,
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 20,
  },
  testButtonText: {
    color: theme.colors.primary,
    fontSize: 14,
    fontWeight: '600',
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  linkButton: {
    marginTop: 20,
    alignItems: 'center',
  },
  linkText: {
    color: theme.colors.primary,
    fontSize: 16,
  },
  disabledText: {
    marginTop: 20,
    textAlign: 'center',
    color: theme.colors.textSecondary,
    fontSize: 14,
    fontStyle: 'italic',
  },
});

