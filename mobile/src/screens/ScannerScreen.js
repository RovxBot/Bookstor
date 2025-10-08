import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
import { booksAPI } from '../services/api';
import { READING_STATUS } from '../config';
import { useMenu } from '../context/MenuContext';
import { useTheme } from '../context/ThemeContext';

export default function ScannerScreen({ navigation }) {
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [loading, setLoading] = useState(false);
  const { openMenu } = useMenu();
  const { theme } = useTheme();

  const styles = createStyles(theme);

  const handleBarCodeScanned = async ({ type, data }) => {
    setScanned(true);
    setLoading(true);

    try {
      // Show options for adding the book
      Alert.alert(
        'Book Found',
        `ISBN: ${data}\n\nHow would you like to add this book?`,
        [
          {
            text: 'Add to Library',
            onPress: () => addBook(data, READING_STATUS.WANT_TO_READ, false),
          },
          {
            text: 'Add to Wishlist',
            onPress: () => addBook(data, READING_STATUS.WISHLIST, true),
          },
          {
            text: 'Cancel',
            onPress: () => {
              setScanned(false);
              setLoading(false);
            },
            style: 'cancel',
          },
        ]
      );
    } catch (error) {
      setLoading(false);
      setScanned(false);
    }
  };

  const addBook = async (isbn, readingStatus, isWishlist) => {
    try {
      const book = await booksAPI.addBookByISBN(isbn, readingStatus, isWishlist);
      setLoading(false);
      
      Alert.alert(
        'Success',
        `"${book.title}" has been added to your ${isWishlist ? 'wishlist' : 'library'}!`,
        [
          {
            text: 'View Book',
            onPress: () => navigation.navigate('BookDetail', { bookId: book.id }),
          },
          {
            text: 'Scan Another',
            onPress: () => setScanned(false),
          },
        ]
      );
    } catch (error) {
      setLoading(false);
      setScanned(false);
      
      const errorMessage = error.response?.data?.detail || 'Failed to add book';
      Alert.alert('Error', errorMessage, [
        {
          text: 'Try Again',
          onPress: () => setScanned(false),
        },
      ]);
    }
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

      <SafeAreaView style={styles.menuButtonContainer} edges={['top']}>
        <TouchableOpacity
          onPress={openMenu}
          style={styles.menuButton}
        >
          <Ionicons name="menu" size={28} color="#fff" />
        </TouchableOpacity>
      </SafeAreaView>

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
  menuButtonContainer: {
    position: 'absolute',
    top: 50,
    left: 20,
    zIndex: 10,
  },
  menuButton: {
    backgroundColor: 'rgba(0, 122, 255, 0.9)',
    padding: 12,
    borderRadius: 8,
  },
  menuIcon: {
    fontSize: 24,
    color: '#fff',
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

