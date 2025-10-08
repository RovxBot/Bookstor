import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Switch,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons, MaterialCommunityIcons, FontAwesome5 } from '@expo/vector-icons';
import { useMenu } from '../context/MenuContext';
import { useTheme } from '../context/ThemeContext';

export default function SettingsScreen({ navigation }) {
  const { openMenu } = useMenu();
  const { theme: currentTheme, themeMode, changeTheme } = useTheme();
  const [oauthProviders, setOauthProviders] = useState({
    entra: { enabled: false, configured: false },
    google: { enabled: false, configured: false },
    github: { enabled: false, configured: false },
  });

  const handleThemeChange = (newTheme) => {
    changeTheme(newTheme);
  };

  const handleOAuthToggle = (provider) => {
    if (!oauthProviders[provider].configured) {
      Alert.alert(
        'Configure OAuth',
        `Please configure ${provider} OAuth settings first.`,
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Configure', onPress: () => handleConfigureOAuth(provider) },
        ]
      );
      return;
    }
    
    setOauthProviders({
      ...oauthProviders,
      [provider]: {
        ...oauthProviders[provider],
        enabled: !oauthProviders[provider].enabled,
      },
    });
  };

  const handleConfigureOAuth = (provider) => {
    // TODO: Navigate to OAuth configuration screen or show modal
    Alert.alert(
      `Configure ${provider.charAt(0).toUpperCase() + provider.slice(1)}`,
      'OAuth configuration will be implemented here.\n\nYou will need:\n- Client ID\n- Client Secret\n- Redirect URI\n- Tenant ID (for Entra)',
      [{ text: 'OK' }]
    );
  };

  const styles = createStyles(currentTheme);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <View style={styles.header}>
        <TouchableOpacity onPress={openMenu} style={styles.menuButton}>
          <Ionicons name="menu" size={28} color={currentTheme.colors.primary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content}>
        {/* Theme Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Appearance</Text>
          <Text style={styles.sectionDescription}>
            Choose how the app looks on your device
          </Text>

          <View style={styles.optionGroup}>
            <TouchableOpacity
              style={[
                styles.themeOption,
                themeMode === 'light' && styles.themeOptionActive,
              ]}
              onPress={() => handleThemeChange('light')}
            >
              <Ionicons
                name="sunny"
                size={24}
                color={themeMode === 'light' ? currentTheme.colors.primary : currentTheme.colors.textSecondary}
              />
              <Text
                style={[
                  styles.themeLabel,
                  themeMode === 'light' && styles.themeLabelActive,
                ]}
              >
                Light Mode
              </Text>
              {themeMode === 'light' && (
                <Ionicons name="checkmark" size={24} color={currentTheme.colors.primary} />
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.themeOption,
                themeMode === 'dark' && styles.themeOptionActive,
              ]}
              onPress={() => handleThemeChange('dark')}
            >
              <Ionicons
                name="moon"
                size={24}
                color={themeMode === 'dark' ? currentTheme.colors.primary : currentTheme.colors.textSecondary}
              />
              <Text
                style={[
                  styles.themeLabel,
                  themeMode === 'dark' && styles.themeLabelActive,
                ]}
              >
                Dark Mode
              </Text>
              {themeMode === 'dark' && (
                <Ionicons name="checkmark" size={24} color={currentTheme.colors.primary} />
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.themeOption,
                themeMode === 'system' && styles.themeOptionActive,
              ]}
              onPress={() => handleThemeChange('system')}
            >
              <Ionicons
                name="phone-portrait"
                size={24}
                color={themeMode === 'system' ? currentTheme.colors.primary : currentTheme.colors.textSecondary}
              />
              <Text
                style={[
                  styles.themeLabel,
                  themeMode === 'system' && styles.themeLabelActive,
                ]}
              >
                Follow System
              </Text>
              {themeMode === 'system' && (
                <Ionicons name="checkmark" size={24} color={currentTheme.colors.primary} />
              )}
            </TouchableOpacity>
          </View>
        </View>

        {/* OAuth Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Single Sign-On (SSO)</Text>
          <Text style={styles.sectionDescription}>
            Enable OAuth providers for authentication
          </Text>

          {/* Microsoft Entra */}
          <View style={styles.oauthItem}>
            <View style={styles.oauthInfo}>
              <MaterialCommunityIcons name="microsoft" size={28} color="#00A4EF" />
              <View style={styles.oauthText}>
                <Text style={styles.oauthName}>Microsoft Entra ID</Text>
                <Text style={styles.oauthStatus}>
                  {oauthProviders.entra.configured
                    ? 'Configured'
                    : 'Not configured'}
                </Text>
              </View>
            </View>
            <View style={styles.oauthActions}>
              <TouchableOpacity
                style={styles.configureButton}
                onPress={() => handleConfigureOAuth('entra')}
              >
                <Text style={styles.configureButtonText}>
                  {oauthProviders.entra.configured ? 'Edit' : 'Setup'}
                </Text>
              </TouchableOpacity>
              <Switch
                value={oauthProviders.entra.enabled}
                onValueChange={() => handleOAuthToggle('entra')}
                disabled={!oauthProviders.entra.configured}
              />
            </View>
          </View>

          {/* Google */}
          <View style={styles.oauthItem}>
            <View style={styles.oauthInfo}>
              <FontAwesome5 name="google" size={24} color="#DB4437" />
              <View style={styles.oauthText}>
                <Text style={styles.oauthName}>Google</Text>
                <Text style={styles.oauthStatus}>
                  {oauthProviders.google.configured
                    ? 'Configured'
                    : 'Not configured'}
                </Text>
              </View>
            </View>
            <View style={styles.oauthActions}>
              <TouchableOpacity
                style={styles.configureButton}
                onPress={() => handleConfigureOAuth('google')}
              >
                <Text style={styles.configureButtonText}>
                  {oauthProviders.google.configured ? 'Edit' : 'Setup'}
                </Text>
              </TouchableOpacity>
              <Switch
                value={oauthProviders.google.enabled}
                onValueChange={() => handleOAuthToggle('google')}
                disabled={!oauthProviders.google.configured}
              />
            </View>
          </View>

          {/* GitHub */}
          <View style={styles.oauthItem}>
            <View style={styles.oauthInfo}>
              <FontAwesome5 name="github" size={24} color={currentTheme.mode === 'dark' ? '#fff' : '#24292e'} />
              <View style={styles.oauthText}>
                <Text style={styles.oauthName}>GitHub</Text>
                <Text style={styles.oauthStatus}>
                  {oauthProviders.github.configured
                    ? 'Configured'
                    : 'Not configured'}
                </Text>
              </View>
            </View>
            <View style={styles.oauthActions}>
              <TouchableOpacity
                style={styles.configureButton}
                onPress={() => handleConfigureOAuth('github')}
              >
                <Text style={styles.configureButtonText}>
                  {oauthProviders.github.configured ? 'Edit' : 'Setup'}
                </Text>
              </TouchableOpacity>
              <Switch
                value={oauthProviders.github.enabled}
                onValueChange={() => handleOAuthToggle('github')}
                disabled={!oauthProviders.github.configured}
              />
            </View>
          </View>
        </View>

        {/* About Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Version</Text>
            <Text style={styles.aboutValue}>1.0.0</Text>
          </View>
          <View style={styles.aboutItem}>
            <Text style={styles.aboutLabel}>Build</Text>
            <Text style={styles.aboutValue}>2024.01</Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const createStyles = (theme) => StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    backgroundColor: theme.colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  menuButton: {
    padding: 5,
  },
  menuIcon: {
    fontSize: 24,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.text,
  },
  placeholder: {
    width: 34,
  },
  content: {
    flex: 1,
  },
  section: {
    backgroundColor: theme.colors.surface,
    marginTop: 20,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
    color: theme.colors.text,
  },
  sectionDescription: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    marginBottom: 15,
  },
  optionGroup: {
    gap: 10,
  },
  themeOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: theme.colors.border,
    backgroundColor: theme.colors.inactive,
  },
  themeOptionActive: {
    borderColor: theme.colors.primary,
    backgroundColor: theme.mode === 'dark' ? theme.colors.card : '#f0f8ff',
  },
  themeIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  themeLabel: {
    fontSize: 16,
    color: theme.colors.text,
    flex: 1,
  },
  themeLabelActive: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  checkmark: {
    fontSize: 20,
    color: theme.colors.primary,
    fontWeight: 'bold',
  },
  oauthItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  oauthInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  oauthIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  oauthText: {
    flex: 1,
  },
  oauthName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 2,
    color: theme.colors.text,
  },
  oauthStatus: {
    fontSize: 12,
    color: theme.colors.textSecondary,
  },
  oauthActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  configureButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: theme.colors.primary,
  },
  configureButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  aboutItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  aboutLabel: {
    fontSize: 16,
    color: theme.colors.text,
  },
  aboutValue: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
});

