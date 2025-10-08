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
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { authAPI } from '../services/api';

export default function LoginScreen({ navigation }) {
  const [serverUrl, setServerUrl] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { theme } = useTheme();

  const styles = createStyles(theme);

  // Load saved server URL on mount
  useEffect(() => {
    const loadServerUrl = async () => {
      const savedUrl = await authAPI.getServerUrl();
      if (savedUrl) {
        setServerUrl(savedUrl);
      }
    };
    loadServerUrl();
  }, []);

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
            onChangeText={setServerUrl}
            autoCapitalize="none"
            keyboardType="url"
          />
          <Text style={styles.hint}>
            Enter the URL of your Bookstor server (e.g., http://192.168.1.100:8000/api)
          </Text>

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

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => navigation.navigate('Register')}
          >
            <Text style={styles.linkText}>
              Don't have an account? Register
            </Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const createStyles = (theme) => StyleSheet.create({
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
    marginBottom: 15,
    fontStyle: 'italic',
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
});

