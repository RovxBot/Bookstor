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
import { useMenu } from '../context/MenuContext';
import { useTheme } from '../context/ThemeContext';

export default function WishlistScreen({ navigation }) {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const { openMenu } = useMenu();
  const { theme } = useTheme();
  const styles = createStyles(theme);

  useEffect(() => {
    loadBooks();
  }, []);

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      loadBooks();
    });
    return unsubscribe;
  }, [navigation]);

  const loadBooks = async () => {
    try {
      setLoading(true);
      const data = await booksAPI.getBooks();
      // Filter for wishlist books only
      const wishlistBooks = data.filter(book => book.is_wishlist);
      setBooks(wishlistBooks);
    } catch (error) {
      Alert.alert('Error', 'Failed to load wishlist');
    } finally {
      setLoading(false);
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
          <Ionicons name="book" size={40} color={theme.colors.textSecondary} />
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

      <Ionicons name="star" size={24} color="#FFD700" />
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={openMenu} style={styles.menuButton}>
          <Ionicons name="menu" size={28} color={theme.colors.text} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>My Wishlist</Text>
        <View style={styles.placeholder} />
      </View>

      {books.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Ionicons name="star-outline" size={80} color={theme.colors.inactive} />
          <Text style={styles.emptyText}>Your wishlist is empty</Text>
          <Text style={styles.emptySubtext}>
            Add books you want to read to your wishlist
          </Text>
        </View>
      ) : (
        <>
          <View style={styles.countContainer}>
            <Text style={styles.countText}>
              {books.length} {books.length === 1 ? 'book' : 'books'} in wishlist
            </Text>
          </View>
          <FlatList
            data={books}
            renderItem={renderBook}
            keyExtractor={(item) => item.id.toString()}
            contentContainerStyle={styles.listContainer}
          />
        </>
      )}
    </View>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  menuButton: {
    padding: 5,
  },
  headerTitle: {
    fontSize: 26,
    fontWeight: '700',
    color: theme.colors.text,
    letterSpacing: 0.3,
  },
  placeholder: {
    width: 38,
  },
  countContainer: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: theme.colors.background,
  },
  countText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    fontWeight: '500',
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
    alignItems: 'center',
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
  bookInfo: {
    flex: 1,
    marginLeft: 15,
    marginRight: 10,
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
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: theme.colors.text,
    marginTop: 20,
    marginBottom: 10,
  },
  emptySubtext: {
    fontSize: 15,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 22,
  },
});

