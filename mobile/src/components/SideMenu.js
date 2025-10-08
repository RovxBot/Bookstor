import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  StyleSheet,
  TouchableWithoutFeedback,
} from 'react-native';
import { Ionicons, MaterialCommunityIcons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

export default function SideMenu({ visible, onClose, navigation, currentScreen }) {
  const { logout } = useAuth();
  const { theme } = useTheme();

  const styles = createStyles(theme);

  const menuItems = [
    { name: 'My Library', iconName: 'library', iconType: 'Ionicons', screen: 'Library' },
    { name: 'Wishlist', iconName: 'star', iconType: 'Ionicons', screen: 'Wishlist' },
    { name: 'Collections', iconName: 'book-multiple', iconType: 'MaterialCommunityIcons', screen: 'Collections' },
    { name: 'Search', iconName: 'search', iconType: 'Ionicons', screen: 'Search' },
    { name: 'Scan Barcode', iconName: 'barcode-scan', iconType: 'MaterialCommunityIcons', screen: 'Scanner' },
    { name: 'Settings', iconName: 'settings', iconType: 'Ionicons', screen: 'Settings' },
  ];

  const renderIcon = (iconName, iconType, isActive) => {
    const color = isActive ? theme.colors.primary : theme.colors.text;
    const IconComponent = iconType === 'Ionicons' ? Ionicons : MaterialCommunityIcons;
    return <IconComponent name={iconName} size={24} color={color} />;
  };

  const handleNavigate = (screen) => {
    onClose();
    if (screen !== currentScreen) {
      navigation.navigate(screen);
    }
  };

  const handleLogout = () => {
    onClose();
    logout();
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
    >
      <TouchableWithoutFeedback onPress={onClose}>
        <View style={styles.overlay}>
          <TouchableWithoutFeedback>
            <View style={styles.menuContainer}>
              <View style={styles.header}>
                <Text style={styles.title}>Bookstor</Text>
                <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                  <Ionicons name="close" size={28} color="#fff" />
                </TouchableOpacity>
              </View>

              <View style={styles.menuContent}>
                {menuItems.map((item) => (
                  <TouchableOpacity
                    key={item.screen}
                    style={[
                      styles.menuItem,
                      currentScreen === item.screen && styles.menuItemActive,
                    ]}
                    onPress={() => handleNavigate(item.screen)}
                  >
                    {renderIcon(item.iconName, item.iconType, currentScreen === item.screen)}
                    <Text
                      style={[
                        styles.menuLabel,
                        currentScreen === item.screen && styles.menuLabelActive,
                      ]}
                    >
                      {item.name}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              <View style={styles.footer}>
                <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
                  <Ionicons name="log-out-outline" size={24} color="#d32f2f" />
                  <Text style={styles.logoutText}>Logout</Text>
                </TouchableOpacity>
              </View>
            </View>
          </TouchableWithoutFeedback>
        </View>
      </TouchableWithoutFeedback>
    </Modal>
  );
}

const createStyles = (theme) => StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    flexDirection: 'row',
  },
  menuContainer: {
    width: 280,
    backgroundColor: theme.colors.surface,
    shadowColor: '#000',
    shadowOffset: { width: 2, height: 0 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  header: {
    padding: 30,
    paddingTop: 60,
    backgroundColor: theme.colors.primary,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#fff',
    letterSpacing: 0.5,
  },
  closeButton: {
    padding: 5,
  },
  closeIcon: {
    fontSize: 24,
    color: '#fff',
    fontWeight: 'bold',
  },
  menuContent: {
    flex: 1,
    paddingTop: 20,
    backgroundColor: theme.colors.surface,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  menuItemActive: {
    backgroundColor: theme.mode === 'dark' ? theme.colors.card : '#f0f8ff',
  },
  menuIcon: {
    fontSize: 24,
    marginRight: 15,
  },
  menuLabel: {
    fontSize: 18,
    color: theme.colors.text,
  },
  menuLabelActive: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  footer: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: theme.colors.border,
    backgroundColor: theme.colors.surface,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: theme.colors.inactive,
    borderRadius: 10,
  },
  logoutIcon: {
    fontSize: 20,
    marginRight: 10,
  },
  logoutText: {
    fontSize: 16,
    color: '#d32f2f',
    fontWeight: '600',
  },
});

