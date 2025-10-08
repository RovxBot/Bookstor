import { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { booksAPI } from '../services/api';
import { useTheme } from '../context/ThemeContext';

export default function CollectionDetailScreen({ route, navigation }) {
  const { collection } = route.params;
  const { theme } = useTheme();
  const styles = createStyles(theme);

  const [missingBooks, setMissingBooks] = useState([]);
  const [loadingMissing, setLoadingMissing] = useState(true);
  const [addingToWishlist, setAddingToWishlist] = useState({});

  useEffect(() => {
    loadMissingBooks();
  }, []);

  const loadMissingBooks = async () => {
    try {
      const data = await booksAPI.getMissingBooks(collection.name);
      setMissingBooks(data.missing_books || []);
    } catch (error) {
      console.error('Failed to load missing books:', error);
    } finally {
      setLoadingMissing(false);
    }
  };

  const addToWishlist = async (book) => {
    setAddingToWishlist(prev => ({ ...prev, [book.title]: true }));

    try {
      // Search for the book
      const searchResults = await booksAPI.searchBooks(`${book.title} ${book.author}`, 5);

      if (searchResults.length === 0) {
        Alert.alert('Not Found', `Could not find "${book.title}" in Google Books.`);
        return;
      }

      // Use the first result
      const bookData = searchResults[0];

      // Add to library as wishlist
      await booksAPI.createBook({
        ...bookData,
        authors: bookData.authors ? bookData.authors.join(', ') : book.author,
        categories: bookData.categories ? bookData.categories.join(', ') : null,
        is_wishlist: true,
        reading_status: 'want_to_read',
      });

      Alert.alert('Success', `"${book.title}" added to your wishlist!`);

      // Remove from missing books list
      setMissingBooks(prev => prev.filter(b => b.title !== book.title));

    } catch (error) {
      console.error('Failed to add to wishlist:', error);
      Alert.alert('Error', 'Failed to add book to wishlist. Please try again.');
    } finally {
      setAddingToWishlist(prev => ({ ...prev, [book.title]: false }));
    }
  };

  const renderBook = ({ item }) => (
    <TouchableOpacity
      style={styles.bookCard}
      onPress={() => navigation.navigate('BookDetail', { bookId: item.id })}
    >
      {item.thumbnail ? (
        <Image source={{ uri: item.thumbnail }} style={styles.thumbnail} />
      ) : (
        <View style={[styles.thumbnail, styles.noThumbnail]}>
          <Text style={styles.noThumbnailText}>📚</Text>
        </View>
      )}

      <View style={styles.bookInfo}>
        <Text style={styles.title} numberOfLines={2}>
          {item.title}
        </Text>
        {item.authors && (
          <Text style={styles.authors} numberOfLines={1}>
            {item.authors}
          </Text>
        )}
        {item.published_date && (
          <Text style={styles.publishedDate}>
            {item.published_date.substring(0, 4)}
          </Text>
        )}
      </View>

      {item.series_position && (
        <View style={styles.positionBadge}>
          <Text style={styles.positionText}>#{item.series_position}</Text>
        </View>
      )}
    </TouchableOpacity>
  );

  const renderMissingBook = ({ item }) => (
    <View style={styles.missingBookCard}>
      <View style={styles.missingBookInfo}>
        <View style={styles.missingBookHeader}>
          <Text style={styles.missingTitle} numberOfLines={2}>
            {item.title}
          </Text>
          {item.position && (
            <View style={styles.missingPositionBadge}>
              <Text style={styles.missingPositionText}>#{item.position}</Text>
            </View>
          )}
        </View>
        {item.author && (
          <Text style={styles.missingAuthors} numberOfLines={1}>
            {item.author}
          </Text>
        )}
      </View>

      <TouchableOpacity
        style={[styles.addButton, addingToWishlist[item.title] && styles.addButtonDisabled]}
        onPress={() => addToWishlist(item)}
        disabled={addingToWishlist[item.title]}
      >
        {addingToWishlist[item.title] ? (
          <ActivityIndicator size="small" color="#fff" />
        ) : (
          <>
            <Ionicons name="add-circle-outline" size={20} color="#fff" />
            <Text style={styles.addButtonText}>Add to Wishlist</Text>
          </>
        )}
      </TouchableOpacity>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.collectionName}>{collection.name}</Text>
        {collection.author && (
          <Text style={styles.author}>by {collection.author}</Text>
        )}
        <Text style={styles.bookCount}>
          {collection.books.length} {collection.books.length === 1 ? 'book' : 'books'}
        </Text>
      </View>

      <FlatList
        data={collection.books}
        renderItem={renderBook}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={styles.listContainer}
        ListFooterComponent={() => (
          <>
            {!loadingMissing && missingBooks.length > 0 && (
              <View style={styles.missingSection}>
                <View style={styles.missingSectionHeader}>
                  <Ionicons name="book-outline" size={24} color={theme.colors.textSecondary} />
                  <Text style={styles.missingSectionTitle}>
                    Missing Books ({missingBooks.length})
                  </Text>
                </View>
                <Text style={styles.missingSectionSubtitle}>
                  Add these books to your wishlist to complete the series
                </Text>

                {missingBooks.map((book, index) => (
                  <View key={index}>
                    {renderMissingBook({ item: book })}
                  </View>
                ))}
              </View>
            )}

            {loadingMissing && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={theme.colors.primary} />
                <Text style={styles.loadingText}>Checking for missing books...</Text>
              </View>
            )}
          </>
        )}
      />
    </View>
  );
}

const createStyles = (theme) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    padding: 20,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  collectionName: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 5,
    color: theme.colors.text,
    letterSpacing: 0.3,
  },
  author: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    marginBottom: 5,
  },
  bookCount: {
    fontSize: 14,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  listContainer: {
    padding: 10,
  },
  bookCard: {
    flexDirection: 'row',
    backgroundColor: theme.colors.card,
    borderRadius: 10,
    padding: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  thumbnail: {
    width: 60,
    height: 90,
    borderRadius: 5,
  },
  noThumbnail: {
    backgroundColor: theme.colors.inactive,
    justifyContent: 'center',
    alignItems: 'center',
  },
  noThumbnailText: {
    fontSize: 30,
  },
  bookInfo: {
    flex: 1,
    marginLeft: 15,
    justifyContent: 'center',
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 5,
    color: theme.colors.text,
  },
  authors: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 3,
  },
  publishedDate: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  positionBadge: {
    backgroundColor: theme.colors.primary,
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 4,
    alignSelf: 'center',
  },
  positionText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  missingSection: {
    marginTop: 20,
    paddingTop: 20,
    borderTopWidth: 2,
    borderTopColor: theme.colors.border,
  },
  missingSectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  missingSectionTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: theme.colors.text,
    marginLeft: 10,
    letterSpacing: 0.3,
  },
  missingSectionSubtitle: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 15,
    fontStyle: 'italic',
  },
  missingBookCard: {
    flexDirection: 'row',
    backgroundColor: theme.colors.card,
    borderRadius: 10,
    padding: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderStyle: 'dashed',
  },
  missingBookInfo: {
    flex: 1,
    justifyContent: 'center',
  },
  missingBookHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 5,
  },
  missingTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: theme.colors.text,
    flex: 1,
  },
  missingPositionBadge: {
    backgroundColor: theme.colors.textSecondary,
    borderRadius: 10,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginLeft: 8,
  },
  missingPositionText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: '600',
  },
  missingAuthors: {
    fontSize: 13,
    color: theme.colors.textSecondary,
  },
  addButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 10,
  },
  addButtonDisabled: {
    opacity: 0.6,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: '600',
    marginLeft: 5,
  },
  loadingContainer: {
    padding: 20,
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 14,
    color: theme.colors.textSecondary,
  },
});

