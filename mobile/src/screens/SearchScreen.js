import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Image,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { booksAPI } from '../services/api';
import { READING_STATUS } from '../config';
import { useMenu } from '../context/MenuContext';
import { useTheme } from '../context/ThemeContext';

export default function SearchScreen({ navigation }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const { openMenu } = useMenu();
  const { theme } = useTheme();

  const styles = createStyles(theme);

  const handleSearch = async () => {
    if (!query.trim()) {
      Alert.alert('Error', 'Please enter a search term');
      return;
    }

    setLoading(true);
    setSearched(true);
    try {
      const data = await booksAPI.searchBooks(query);
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
      Alert.alert('Error', 'Failed to search books. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddBook = async (book) => {
    Alert.alert(
      'Add Book',
      `Add "${book.title}" to your library?`,
      [
        {
          text: 'Add to Library',
          onPress: () => addBook(book, READING_STATUS.WANT_TO_READ, false),
        },
        {
          text: 'Add to Wishlist',
          onPress: () => addBook(book, READING_STATUS.WISHLIST, true),
        },
        {
          text: 'Cancel',
          style: 'cancel',
        },
      ]
    );
  };

  const addBook = async (book, readingStatus, isWishlist) => {
    try {
      const bookData = {
        title: book.title,
        authors: book.authors ? book.authors.join(', ') : null,
        description: book.description,
        publisher: book.publisher,
        published_date: book.published_date,
        page_count: book.page_count,
        categories: book.categories ? book.categories.join(', ') : null,
        thumbnail: book.thumbnail,
        isbn: book.isbn,
        google_books_id: book.google_books_id,
        reading_status: readingStatus,
        is_wishlist: isWishlist,
      };

      const addedBook = await booksAPI.addBookManually(bookData);
      
      Alert.alert(
        'Success',
        `"${book.title}" has been added to your ${isWishlist ? 'wishlist' : 'library'}!`,
        [
          {
            text: 'View Book',
            onPress: () => navigation.navigate('BookDetail', { bookId: addedBook.id }),
          },
          {
            text: 'Search More',
            style: 'cancel',
          },
        ]
      );
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to add book';
      Alert.alert('Error', errorMessage);
    }
  };

  const renderBook = ({ item }) => (
    <TouchableOpacity
      style={styles.bookCard}
      onPress={() => handleAddBook(item)}
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
        {item.authors && item.authors.length > 0 && (
          <Text style={styles.authors} numberOfLines={1}>
            {item.authors.join(', ')}
          </Text>
        )}
        {item.published_date && (
          <Text style={styles.publishedDate}>
            {item.published_date.substring(0, 4)}
          </Text>
        )}
      </View>
      
      <View style={styles.addButton}>
        <Text style={styles.addButtonText}>+</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.flex}
      >
        <View style={styles.header}>
          <TouchableOpacity
            onPress={openMenu}
            style={styles.menuButton}
          >
            <Ionicons name="menu" size={28} color={theme.colors.primary} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Search Books</Text>
          <View style={styles.placeholder} />
        </View>

      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search by title or author..."
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
        />
        <TouchableOpacity
          style={styles.searchButton}
          onPress={handleSearch}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.searchButtonText}>Search</Text>
          )}
        </TouchableOpacity>
      </View>

      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
        </View>
      ) : searched && results.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>🔍</Text>
          <Text style={styles.emptyTitle}>No books found</Text>
          <Text style={styles.emptySubtitle}>
            Try a different search term
          </Text>
        </View>
      ) : !searched ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>📖</Text>
          <Text style={styles.emptyTitle}>Search for Books</Text>
          <Text style={styles.emptySubtitle}>
            Enter a title or author to find books
          </Text>
        </View>
      ) : (
        <FlatList
          data={results}
          renderItem={renderBook}
          keyExtractor={(item, index) => item.google_books_id || index.toString()}
          contentContainerStyle={styles.listContainer}
        />
      )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const createStyles = (theme) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  flex: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  menuButton: {
    padding: 8,
  },
  menuIcon: {
    fontSize: 24,
    color: theme.colors.primary,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    flex: 1,
    textAlign: 'center',
    color: theme.colors.text,
  },
  placeholder: {
    width: 40,
  },
  searchContainer: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  searchInput: {
    flex: 1,
    backgroundColor: theme.colors.inactive,
    padding: 12,
    borderRadius: 10,
    fontSize: 16,
    marginRight: 10,
    color: theme.colors.text,
  },
  searchButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    minWidth: 80,
  },
  searchButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    fontSize: 80,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: theme.colors.text,
  },
  emptySubtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
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
    fontWeight: 'bold',
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
    color: theme.colors.placeholder,
  },
  addButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: theme.colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
  },
  addButtonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
});

