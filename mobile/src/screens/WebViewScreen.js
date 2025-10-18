import React, { useRef, useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ActivityIndicator,
  Alert,
  BackHandler,
} from 'react-native';
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useTheme } from '../context/ThemeContext';

export default function WebViewScreen({ navigation }) {
  const webViewRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [serverUrl, setServerUrl] = useState(null);
  const [canGoBack, setCanGoBack] = useState(false);
  const { theme, isDark } = useTheme();

  const styles = createStyles(theme);

  // Load server URL and establish web session on mount
  useEffect(() => {
    initializeWebView();
  }, []);

  const initializeWebView = async () => {
    await loadServerUrl();
    await establishWebSession();
  };

  // Handle Android back button
  useEffect(() => {
    const backHandler = BackHandler.addEventListener('hardwareBackPress', () => {
      if (canGoBack && webViewRef.current) {
        webViewRef.current.goBack();
        return true; // Prevent default behaviour
      }
      return false; // Let default behaviour happen (exit app)
    });

    return () => backHandler.remove();
  }, [canGoBack]);

  const loadServerUrl = async () => {
    try {
      const url = await AsyncStorage.getItem('serverUrl');
      if (url) {
        // Remove /api suffix if present (WebView needs base URL)
        const baseUrl = url.replace(/\/api\/?$/, '');
        setServerUrl(baseUrl);
      } else {
        Alert.alert('Error', 'Server URL not configured');
        navigation.navigate('Login');
      }
    } catch (error) {
      console.error('Failed to load server URL:', error);
      Alert.alert('Error', 'Failed to load server configuration');
    }
  };

  // Establish web session using JWT token
  // This will be called via injected JavaScript in the WebView
  const establishWebSession = async () => {
    try {
      const token = await AsyncStorage.getItem('token');

      if (!token) {
        console.log('No token, skipping session establishment');
        return null;
      }

      return token;
    } catch (error) {
      console.error('Failed to get token:', error);
      return null;
    }
  };

  // Handle messages from WebView
  const handleMessage = (event) => {
    try {
      const message = JSON.parse(event.nativeEvent.data);
      console.log('Received message from WebView:', message);

      switch (message.type) {
        case 'OPEN_SCANNER':
          // Navigate to scanner screen with WebView ref
          navigation.navigate('Scanner', { webViewRef });
          break;

        case 'LOGOUT':
          // Handle logout
          handleLogout();
          break;

        default:
          console.log('Unknown message type:', message.type);
      }
    } catch (error) {
      console.error('Error parsing message from WebView:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('token');
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' }],
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  // Get injected JavaScript with token
  const getInjectedJavaScript = async () => {
    const token = await establishWebSession();

    return `
      (function() {
        // Set up React Native WebView flag
        window.isReactNativeWebView = true;

        // Log that we're in WebView
        console.log('Running in React Native WebView');

        // Apply theme from React Native
        const theme = '${isDark ? 'dark' : 'light'}';
        if (window.applyTheme) {
          window.applyTheme(theme);
        }

        // Establish web session with JWT token
        const token = '${token || ''}';
        if (token) {
          console.log('Establishing web session...');
          fetch('/api/auth/create-web-session', {
            method: 'POST',
            headers: {
              'Authorization': 'Bearer ' + token,
              'Content-Type': 'application/json'
            },
            credentials: 'include'
          })
          .then(response => {
            if (response.ok) {
              console.log('Web session established successfully');
            } else {
              console.error('Failed to establish web session:', response.status);
            }
          })
          .catch(error => {
            console.error('Error establishing web session:', error);
          });
        }

        // Override console.log to send to React Native (for debugging)
        const originalLog = console.log;
        console.log = function(...args) {
          originalLog.apply(console, args);
          try {
            window.ReactNativeWebView.postMessage(JSON.stringify({
              type: 'CONSOLE_LOG',
              message: args.join(' ')
            }));
          } catch (e) {}
        };

        true; // Required for injectedJavaScript
      })();
    `;
  };

  // State for injected JavaScript
  const [injectedJS, setInjectedJS] = useState('');

  // Load injected JavaScript on mount
  useEffect(() => {
    const loadInjectedJS = async () => {
      const js = await getInjectedJavaScript();
      setInjectedJS(js);
    };
    loadInjectedJS();
  }, [isDark]);

  // Handle navigation state changes
  const handleNavigationStateChange = (navState) => {
    setCanGoBack(navState.canGoBack);
  };

  // Handle load end
  const handleLoadEnd = () => {
    setLoading(false);
  };

  // Handle errors
  const handleError = (syntheticEvent) => {
    const { nativeEvent } = syntheticEvent;
    console.error('WebView error:', nativeEvent);
    Alert.alert(
      'Connection Error',
      'Failed to load the page. Please check your server connection.',
      [
        { text: 'Retry', onPress: () => webViewRef.current?.reload() },
        { text: 'Settings', onPress: () => navigation.navigate('Login') },
      ]
    );
  };

  if (!serverUrl || !injectedJS) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <WebView
        ref={webViewRef}
        source={{ uri: `${serverUrl}/app/library` }}
        style={styles.webview}
        onMessage={handleMessage}
        onNavigationStateChange={handleNavigationStateChange}
        onLoadEnd={handleLoadEnd}
        onError={handleError}
        injectedJavaScript={injectedJS}
        // WebView configuration
        javaScriptEnabled={true}
        domStorageEnabled={true}
        startInLoadingState={true}
        scalesPageToFit={true}
        allowsBackForwardNavigationGestures={true}
        // Cookie and cache settings
        sharedCookiesEnabled={true}
        thirdPartyCookiesEnabled={true}
        cacheEnabled={true}
        // User agent - identify as mobile browser
        userAgent="Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 BookstorApp/0.0.3"
        // Rendering
        renderLoading={() => (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={theme.colors.primary} />
          </View>
        )}
        // Allow file access for images
        allowFileAccess={true}
        allowUniversalAccessFromFileURLs={true}
        // Media playback
        mediaPlaybackRequiresUserAction={false}
        // Geolocation (if needed in future)
        geolocationEnabled={false}
      />
      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      )}
    </View>
  );
}

const createStyles = (theme) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  webview: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
});

