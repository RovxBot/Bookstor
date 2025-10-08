import React, { useState, useRef } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuth } from '../context/AuthContext';
import { useMenu } from '../context/MenuContext';
import SideMenu from '../components/SideMenu';

// Screens
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import LibraryScreen from '../screens/LibraryScreen';
import WishlistScreen from '../screens/WishlistScreen';
import ScannerScreen from '../screens/ScannerScreen';
import SearchScreen from '../screens/SearchScreen';
import CollectionsScreen from '../screens/CollectionsScreen';
import CollectionDetailScreen from '../screens/CollectionDetailScreen';
import BookDetailScreen from '../screens/BookDetailScreen';
import SettingsScreen from '../screens/SettingsScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Hidden tab navigator (no visible tabs)
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: { display: 'none' }, // Hide the tab bar
      }}
    >
      <Tab.Screen name="Library" component={LibraryScreen} />
      <Tab.Screen name="Wishlist" component={WishlistScreen} />
      <Tab.Screen name="Collections" component={CollectionsScreen} />
      <Tab.Screen name="Search" component={SearchScreen} />
      <Tab.Screen name="Scanner" component={ScannerScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

function MainStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="MainTabs"
        component={MainTabs}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="BookDetail"
        component={BookDetailScreen}
        options={{ title: 'Book Details' }}
      />
      <Stack.Screen
        name="CollectionDetail"
        component={CollectionDetailScreen}
        options={{ title: 'Collection' }}
      />
    </Stack.Navigator>
  );
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  const { user, loading } = useAuth();
  const { menuVisible, closeMenu } = useMenu();
  const navigationRef = useRef();
  const [currentScreen, setCurrentScreen] = useState('Library');

  if (loading) {
    return null; // Or a loading screen
  }

  return (
    <>
      <NavigationContainer
        ref={navigationRef}
        onStateChange={() => {
          const currentRoute = navigationRef.current?.getCurrentRoute();
          if (currentRoute) {
            setCurrentScreen(currentRoute.name);
          }
        }}
      >
        {user ? <MainStack /> : <AuthStack />}
      </NavigationContainer>
      {user && (
        <SideMenu
          visible={menuVisible}
          onClose={closeMenu}
          navigation={navigationRef.current}
          currentScreen={currentScreen}
        />
      )}
    </>
  );
}

