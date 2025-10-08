import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Image,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { booksAPI } from '../services/api';
import { useMenu } from '../context/MenuContext';
import { useTheme } from '../context/ThemeContext';

export default function CollectionsScreen({ navigation }) {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { openMenu } = useMenu();
  const { theme } = useTheme();

  const styles = createStyles(theme);

  useFocusEffect(
    useCallback(() => {
      loadCollections();
    }, [])
  );

  const loadCollections = async () => {
    try {
      const data = await booksAPI.getCollections();
      setCollections(data);
    } catch (error) {
      console.error('Failed to load collections:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadCollections();
  };

  const renderCollection = ({ item }) => (
    <TouchableOpacity
      style={styles.collectionCard}
      onPress={() => navigation.navigate('CollectionDetail', { collection: item })}
    >
      <View style={styles.thumbnailContainer}>
        {item.books.slice(0, 4).map((book, index) => (
          book.thumbnail ? (
            <Image
              key={index}
              source={{ uri: book.thumbnail }}
              style={[
                styles.miniThumbnail,
                index === 1 && styles.miniThumbnailTopRight,
                index === 2 && styles.miniThumbnailBottomLeft,
                index === 3 && styles.miniThumbnailBottomRight,
              ]}
            />
          ) : null
        ))}
        {item.books.length === 0 && (
          <View style={styles.noThumbnail}>
            <Text style={styles.noThumbnailText}>📚</Text>
          </View>
        )}
      </View>
      
      <View style={styles.collectionInfo}>
        <Text style={styles.collectionName} numberOfLines={2}>
          {item.name}
        </Text>
        <Text style={styles.bookCount}>
          {item.books.length} {item.books.length === 1 ? 'book' : 'books'}
        </Text>
        {item.author && (
          <Text style={styles.author} numberOfLines={1}>
            by {item.author}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity
          onPress={openMenu}
          style={styles.menuButton}
        >
          <Ionicons name="menu" size={28} color={theme.colors.primary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Collections</Text>
        <View style={styles.placeholder} />
      </View>

      {collections.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>📚</Text>
          <Text style={styles.emptyTitle}>No collections yet</Text>
          <Text style={styles.emptySubtitle}>
            Add books from a series to see them grouped here
          </Text>
        </View>
      ) : (
        <FlatList
          data={collections}
          renderItem={renderCollection}
          keyExtractor={(item) => item.name}
          contentContainerStyle={styles.listContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        />
      )}
    </SafeAreaView>
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
  listContainer: {
    padding: 10,
  },
  collectionCard: {
    flexDirection: 'row',
    backgroundColor: theme.colors.card,
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  thumbnailContainer: {
    width: 100,
    height: 100,
    borderRadius: 5,
    overflow: 'hidden',
    backgroundColor: theme.colors.inactive,
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  miniThumbnail: {
    width: 50,
    height: 50,
  },
  miniThumbnailTopRight: {
    position: 'absolute',
    top: 0,
    right: 0,
  },
  miniThumbnailBottomLeft: {
    position: 'absolute',
    bottom: 0,
    left: 0,
  },
  miniThumbnailBottomRight: {
    position: 'absolute',
    bottom: 0,
    right: 0,
  },
  noThumbnail: {
    width: 100,
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.inactive,
  },
  noThumbnailText: {
    fontSize: 40,
  },
  collectionInfo: {
    flex: 1,
    marginLeft: 15,
    justifyContent: 'center',
  },
  collectionName: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
    color: theme.colors.text,
  },
  bookCount: {
    fontSize: 14,
    color: theme.colors.primary,
    marginBottom: 3,
  },
  author: {
    fontSize: 14,
    color: theme.colors.textSecondary,
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
});

