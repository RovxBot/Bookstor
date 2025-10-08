import { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Image,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  Dimensions,
  ImageBackground,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import { booksAPI } from '../services/api';
import { READING_STATUS, READING_STATUS_LABELS } from '../config';
import { useTheme } from '../context/ThemeContext';

const { width } = Dimensions.get('window');

export default function BookDetailScreen({ route, navigation }) {
  const { bookId } = route.params;
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notes, setNotes] = useState('');
  const { theme } = useTheme();

  const styles = createStyles(theme);

  useEffect(() => {
    loadBook();
  }, [bookId]);

  const loadBook = async () => {
    try {
      const data = await booksAPI.getBook(bookId);
      setBook(data);
      setNotes(data.notes || '');
    } catch (error) {
      Alert.alert('Error', 'Failed to load book details');
      navigation.goBack();
    } finally {
      setLoading(false);
    }
  };

  const updateReadingStatus = async (newStatus) => {
    try {
      const updated = await booksAPI.updateBook(bookId, {
        reading_status: newStatus,
      });
      setBook(updated);
      Alert.alert('Success', 'Reading status updated');
    } catch (error) {
      Alert.alert('Error', 'Failed to update reading status');
    }
  };

  const saveNotes = async () => {
    try {
      const updated = await booksAPI.updateBook(bookId, { notes });
      setBook(updated);
      setEditingNotes(false);
      Alert.alert('Success', 'Notes saved');
    } catch (error) {
      Alert.alert('Error', 'Failed to save notes');
    }
  };

  const toggleWishlist = async () => {
    try {
      const updated = await booksAPI.updateBook(bookId, {
        is_wishlist: !book.is_wishlist,
      });
      setBook(updated);
    } catch (error) {
      Alert.alert('Error', 'Failed to update wishlist status');
    }
  };

  const deleteBook = () => {
    Alert.alert(
      'Delete Book',
      'Are you sure you want to remove this book from your library?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await booksAPI.deleteBook(bookId);
              navigation.goBack();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete book');
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Netflix-style Hero Section */}
      <View style={styles.heroContainer}>
        {book.thumbnail ? (
          <ImageBackground
            source={{ uri: book.thumbnail }}
            style={styles.heroImage}
            blurRadius={10}
          >
            <LinearGradient
              colors={['transparent', 'rgba(0,0,0,0.7)', theme.colors.background]}
              style={styles.heroGradient}
            >
              <View style={styles.heroContent}>
                <Image source={{ uri: book.thumbnail }} style={styles.coverImage} />
                <View style={styles.heroInfo}>
                  <Text style={styles.title}>{book.title}</Text>
                  {book.authors && (
                    <Text style={styles.authors}>{book.authors}</Text>
                  )}
                  <View style={styles.metadataRow}>
                    {book.published_date && (
                      <Text style={styles.metadataItem}>
                        {book.published_date.substring(0, 4)}
                      </Text>
                    )}
                    {book.page_count && (
                      <Text style={styles.metadataItem}>{book.page_count} pages</Text>
                    )}
                  </View>
                </View>
              </View>
            </LinearGradient>
          </ImageBackground>
        ) : (
          <View style={styles.heroPlaceholder}>
            <LinearGradient
              colors={[theme.colors.surface, theme.colors.background]}
              style={styles.heroGradient}
            >
              <View style={styles.heroContent}>
                <View style={[styles.coverImage, styles.noCover]}>
                  <Ionicons name="book" size={80} color={theme.colors.textSecondary} />
                </View>
                <View style={styles.heroInfo}>
                  <Text style={styles.title}>{book.title}</Text>
                  {book.authors && (
                    <Text style={styles.authors}>{book.authors}</Text>
                  )}
                  <View style={styles.metadataRow}>
                    {book.published_date && (
                      <Text style={styles.metadataItem}>
                        {book.published_date.substring(0, 4)}
                      </Text>
                    )}
                    {book.page_count && (
                      <Text style={styles.metadataItem}>{book.page_count} pages</Text>
                    )}
                  </View>
                </View>
              </View>
            </LinearGradient>
          </View>
        )}
      </View>

      {/* Action Buttons */}
      <View style={styles.actionSection}>
        <TouchableOpacity
          style={[styles.wishlistButton, book.is_wishlist && styles.wishlistButtonActive]}
          onPress={toggleWishlist}
        >
          <Ionicons
            name={book.is_wishlist ? "star" : "star-outline"}
            size={20}
            color={book.is_wishlist ? "#FFD700" : theme.colors.text}
          />
          <Text style={styles.wishlistButtonText}>
            {book.is_wishlist ? 'In Wishlist' : 'Add to Wishlist'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Reading Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Reading Status</Text>
        <View style={styles.statusButtons}>
          {Object.entries(READING_STATUS).map(([key, value]) => (
            <TouchableOpacity
              key={value}
              style={[
                styles.statusButton,
                book.reading_status === value && styles.statusButtonActive,
              ]}
              onPress={() => updateReadingStatus(value)}
            >
              <Text
                style={[
                  styles.statusButtonText,
                  book.reading_status === value && styles.statusButtonTextActive,
                ]}
              >
                {READING_STATUS_LABELS[value]}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {book.description && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Description</Text>
          <Text style={styles.description}>{book.description}</Text>
        </View>
      )}

      <View style={styles.section}>
        <View style={styles.notesHeader}>
          <Text style={styles.sectionTitle}>Notes</Text>
          {!editingNotes && (
            <TouchableOpacity onPress={() => setEditingNotes(true)}>
              <Text style={styles.editButton}>Edit</Text>
            </TouchableOpacity>
          )}
        </View>
        
        {editingNotes ? (
          <>
            <TextInput
              style={styles.notesInput}
              value={notes}
              onChangeText={setNotes}
              placeholder="Add your notes here..."
              multiline
              numberOfLines={6}
            />
            <View style={styles.notesActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => {
                  setNotes(book.notes || '');
                  setEditingNotes(false);
                }}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.saveButton} onPress={saveNotes}>
                <Text style={styles.saveButtonText}>Save</Text>
              </TouchableOpacity>
            </View>
          </>
        ) : (
          <Text style={styles.notesText}>
            {book.notes || 'No notes yet. Tap Edit to add notes.'}
          </Text>
        )}
      </View>

      <TouchableOpacity style={styles.deleteButton} onPress={deleteBook}>
        <Text style={styles.deleteButtonText}>Delete Book</Text>
      </TouchableOpacity>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

const createStyles = (theme) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  // Netflix-style Hero Section
  heroContainer: {
    width: '100%',
    height: 500,
  },
  heroImage: {
    width: '100%',
    height: '100%',
  },
  heroPlaceholder: {
    width: '100%',
    height: '100%',
    backgroundColor: theme.colors.surface,
  },
  heroGradient: {
    flex: 1,
    justifyContent: 'flex-end',
  },
  heroContent: {
    padding: 20,
    paddingBottom: 30,
    alignItems: 'center',
  },
  coverImage: {
    width: 160,
    height: 240,
    borderRadius: 8,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  noCover: {
    backgroundColor: theme.colors.inactive,
    justifyContent: 'center',
    alignItems: 'center',
  },
  heroInfo: {
    alignItems: 'center',
    width: '100%',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
    color: '#fff',
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.75)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
    letterSpacing: 0.5,
  },
  authors: {
    fontSize: 18,
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: 12,
    textAlign: 'center',
    textShadowColor: 'rgba(0, 0, 0, 0.75)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  metadataRow: {
    flexDirection: 'row',
    gap: 15,
  },
  metadataItem: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
    textShadowColor: 'rgba(0, 0, 0, 0.75)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 3,
  },
  // Action Buttons
  actionSection: {
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: theme.colors.background,
  },
  wishlistButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 15,
    borderRadius: 8,
    backgroundColor: theme.colors.surface,
    gap: 8,
  },
  wishlistButtonActive: {
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: '#FFD700',
  },
  wishlistButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
  },
  // Sections
  section: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    backgroundColor: theme.colors.background,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 15,
    color: theme.colors.text,
    letterSpacing: 0.3,
  },
  statusButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  statusButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  statusButtonActive: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  statusButtonText: {
    fontSize: 14,
    color: theme.colors.text,
    fontWeight: '500',
  },
  statusButtonTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  description: {
    fontSize: 15,
    lineHeight: 24,
    color: theme.colors.textSecondary,
  },
  notesHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  editButton: {
    color: theme.colors.primary,
    fontSize: 16,
    fontWeight: '600',
  },
  notesInput: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
    minHeight: 120,
    textAlignVertical: 'top',
    backgroundColor: theme.colors.surface,
    color: theme.colors.text,
  },
  notesActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 10,
    gap: 10,
  },
  cancelButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  cancelButtonText: {
    color: theme.colors.textSecondary,
    fontSize: 16,
  },
  saveButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  notesText: {
    fontSize: 15,
    lineHeight: 24,
    color: theme.colors.textSecondary,
  },
  deleteButton: {
    backgroundColor: theme.colors.surface,
    padding: 15,
    marginHorizontal: 20,
    marginTop: 10,
    marginBottom: 20,
    alignItems: 'center',
    borderRadius: 8,
  },
  deleteButtonText: {
    color: '#ff3b30',
    fontSize: 16,
    fontWeight: '600',
  },
});

