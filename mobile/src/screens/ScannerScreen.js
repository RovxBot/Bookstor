import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useTheme } from '../context/ThemeContext';

export default function ScannerScreen({ navigation, route }) {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [loading, setLoading] = useState(false);
  const { theme } = useTheme();

  const styles = createStyles(theme);

  // Get the WebView ref from route params (if passed)
  const webViewRef = route?.params?.webViewRef;

  const handleBarCodeScanned = async ({ data }) => {
    setScanned(true);
    setLoading(false);

    // Show options for adding the book
    Alert.alert(
      'Book Scanned',
      `ISBN: ${data}\n\nHow would you like to add this book?`,
      [
        {
          text: 'Add to Library',
          onPress: () => sendToWebView(data, false),
        },
        {
          text: 'Add to Wishlist',
          onPress: () => sendToWebView(data, true),
        },
        {
          text: 'Cancel',
          onPress: () => {
            setScanned(false);
            navigation.goBack();
          },
          style: 'cancel',
        },
      ]
    );
  };

  // Send scanned ISBN to WebView
  const sendToWebView = (isbn, addToWishlist) => {
    // Send message to WebView via navigation params
    if (webViewRef && webViewRef.current) {
      // Inject JavaScript to handle the scanned ISBN
      webViewRef.current.injectJavaScript(`
        window.handleScannedISBN('${isbn}', ${addToWishlist});
      `);

      console.log('Sent ISBN to WebView:', isbn);
    }

    // Navigate back to WebView
    navigation.goBack();
  };

  if (!permission) {
    // Camera permissions are still loading
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Requesting camera permission...</Text>
      </View>
    );
  }

  if (!permission.granted) {
    // Camera permissions are not granted yet
    return (
      <View style={styles.container}>
        <Text style={styles.text}>No access to camera</Text>
        <TouchableOpacity
          style={styles.button}
          onPress={requestPermission}
        >
          <Text style={styles.buttonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <CameraView
        style={StyleSheet.absoluteFillObject}
        facing="back"
        onBarcodeScanned={scanned ? undefined : handleBarCodeScanned}
        barcodeScannerSettings={{
          barcodeTypes: ['ean13', 'ean8', 'upc_a', 'upc_e', 'code128', 'code39'],
        }}
      />

      <View style={styles.overlay}>
        <View style={styles.topOverlay} />
        <View style={styles.middleRow}>
          <View style={styles.sideOverlay} />
          <View style={styles.scanArea} />
          <View style={styles.sideOverlay} />
        </View>
        <View style={styles.bottomOverlay}>
          <Text style={styles.instructions}>
            {loading ? 'Adding book...' : 'Align barcode within the frame'}
          </Text>
          {loading && <ActivityIndicator size="large" color="#fff" />}
          {scanned && !loading && (
            <TouchableOpacity
              style={styles.button}
              onPress={() => setScanned(false)}
            >
              <Text style={styles.buttonText}>Tap to Scan Again</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
}

const createStyles = (theme) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  overlay: {
    flex: 1,
  },
  topOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
  },
  middleRow: {
    flexDirection: 'row',
    height: 250,
  },
  sideOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
  },
  scanArea: {
    width: 250,
    borderWidth: 2,
    borderColor: theme.colors.primary,
    backgroundColor: 'transparent',
  },
  bottomOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  instructions: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  text: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 20,
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 15,
    borderRadius: 10,
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

