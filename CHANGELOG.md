# Changelog

All notable changes to Bookstor will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.0.5] - 2025-10-19

### Added
- Netflix-style library UI with horizontal scrolling rows organised by reading status
- Grid layout for search and filter results
- Advanced search functionality with real-time filtering by title, author, and category
- Status filter buttons (All Books, Reading, Want to Read, Finished)
- Dynamic API integration management system via admin panel
- Hardcover API integration support with GraphQL
- Wishlist "Purchased" button to move books from wishlist to library
- Optimised horizontal scrolling with 25x multiplier for trackpad
- Shift+Scroll for alternative horizontal scrolling method

### Changed
- Library page now uses horizontal scrolling rows instead of grid by default
- Search/filter results display in grid layout for better visibility
- Improved barcode scanner dialog with clearer messaging
- Enhanced scroll performance by removing smooth scrolling animation
- Updated "Remove from Wishlist" to "Purchased" with shopping cart icon

### Fixed
- Vertical page scrolling now works correctly when hovering over book rows
- Wishlist button functionality now works properly
- Barcode scanner now correctly adds books to library or wishlist based on user choice

### Removed
- Removed all test scripts from repository (test_*.py files)
- Removed duplicate ADMIN_PANEL.md documentation

## [v0.0.4] - 2025-10-18

### Fixed
- Fixed mobile app login redirect issue where `/api/app/library` was returning 404
- Fixed WebView URL handling to properly strip `/api` suffix from server URL
- Fixed authentication redirect in `/app/library` route to use proper RedirectResponse
- Improved session cookie handling for mobile WebView authentication

### Changed
- Updated `require_user()` function to return proper 401 error instead of malformed redirect
- Enhanced WebView initialization to handle server URLs with or without `/api` suffix

## [v0.0.3] - 2025-10-17

### 🎉 Major Architecture Change: WebView-Based Mobile App

This release represents a fundamental shift in the mobile app architecture, moving from a fully native React Native UI to a WebView-based approach. This change dramatically reduces code duplication and maintenance overhead while providing a consistent experience across web and mobile platforms.

### Added

#### Web App Enhancements
- **Mobile WebView Support**: Added comprehensive mobile WebView detection and optimisation
- **Mobile Bottom Navigation**: Responsive bottom navigation bar for mobile devices (≤768px)
- **Mobile Header**: Fixed header with app branding for mobile view
- **Floating Action Button (FAB)**: Scanner button visible only in mobile WebView
- **JavaScript Bridge**: Bidirectional communication between React Native and WebView
  - `window.sendToNative()` - Send messages from web to native
  - `window.openScanner()` - Trigger native barcode scanner
  - `window.handleScannedISBN()` - Process scanned barcodes from native scanner
- **Session Bridge Endpoint**: `/api/auth/create-web-session` - Converts JWT tokens to session cookies

#### Mobile App Features
- **WebView Container**: New `WebViewScreen.js` component that loads the web app
- **Authentication Flow**: Seamless JWT to session cookie conversion
- **Native Scanner Integration**: Scanner sends ISBN data directly to WebView via JavaScript injection
- **Theme Synchronisation**: React Native theme applied to WebView content

#### Responsive Design Improvements
- **Mobile Grid Layouts**: 2-column grid on mobile (≤768px), 1-column on very small screens (≤400px)
- **Touch Optimisations**: 44px minimum tap targets, active states instead of hover
- **Responsive Typography**: Scaled font sizes for mobile devices
- **Responsive Images**: Smaller book covers on mobile (280px → 220px)
- **Horizontal Scrolling**: Filter bars and tabs scroll horizontally on mobile
- **Better Spacing**: Reduced padding and gaps on mobile devices

#### Dark Mode Enhancements
- **Status Badge Dark Mode**: Improved status badge colours with transparency
  - Want to Read: Blue with transparency
  - Currently Reading: Green with transparency
  - Read: Purple with transparency
- **Wishlist Badge Dark Mode**: Better visibility in dark theme

### Changed

#### Mobile App Architecture
- **Simplified Navigation**: Reduced from 10 screens to 4 screens
  - Kept: LoginScreen, RegisterScreen, WebViewScreen, ScannerScreen
  - Removed: LibraryScreen, WishlistScreen, CollectionsScreen, CollectionDetailScreen, SearchScreen, BookDetailScreen, SettingsScreen
- **Simplified AppNavigator**: Reduced from 109 lines to 60 lines (45% reduction)
- **Removed Tab Navigator**: Now uses simple stack navigator only
- **Removed SideMenu**: No longer needed with WebView approach

#### API Changes
- **Minimal API Functions**: Reduced from 17 functions to 9 functions
  - Kept all authentication functions (8 functions)
  - Kept only `addBookByISBN` for scanner (1 function)
  - Removed: searchBooks, getBooks, getBook, addBookManually, updateBook, deleteBook, getCollections, getMissingBooks

#### UI/UX Improvements
- **Consistent Border Radius**: Using CSS variables throughout
- **Better Text Truncation**: Improved `-webkit-line-clamp` usage
- **Touch-Friendly Buttons**: Larger tap targets on mobile
- **Improved Loading States**: Better spinner styling and positioning
- **Better Empty States**: Improved messaging and styling

### Removed

#### Mobile App Code Cleanup
- **Deleted 7 React Native Screens**: ~2,000 lines of duplicate UI code
  - LibraryScreen.js (~300 lines)
  - WishlistScreen.js (~250 lines)
  - CollectionsScreen.js (~200 lines)
  - CollectionDetailScreen.js (~250 lines)
  - SearchScreen.js (~300 lines)
  - BookDetailScreen.js (~400 lines)
  - SettingsScreen.js (~200 lines)
- **Deleted Components**: SideMenu.js (~150 lines)
- **Deleted Context**: MenuContext.js (~25 lines)
- **Removed Dependencies**: 
  - `@react-navigation/bottom-tabs` (no longer using tab navigator)
  - `expo-linear-gradient` (not used)
  - `expo-font` (not used)

### Fixed

#### Responsive Design Issues
- **Mobile Grid Layouts**: Fixed book card grids to display properly on mobile
- **Filter Bar Overflow**: Fixed horizontal scrolling on mobile filter bars
- **Search Form Layout**: Fixed stacked layout on mobile devices
- **Tab Overflow**: Fixed horizontal scrolling for tabs on mobile
- **Touch Interactions**: Fixed hover effects on touch devices

#### Dark Mode Issues
- **Status Badge Contrast**: Improved contrast in dark mode
- **Wishlist Badge Visibility**: Better visibility in dark theme
- **Component Consistency**: All components now properly support dark mode

### Technical Details

#### Code Reduction Statistics
- **Total Lines Removed**: ~2,125 lines of code
- **Mobile Screens**: 10 → 4 (60% reduction)
- **AppNavigator**: 109 → 60 lines (45% reduction)
- **API Functions**: 185 → 136 lines (26% reduction)
- **Dependencies**: 30 → 27 packages (10% reduction)

#### Architecture Benefits
- ✅ Single UI codebase (web app is source of truth)
- ✅ Reduced maintenance overhead
- ✅ Smaller APK size
- ✅ Faster development (features only need web implementation)
- ✅ Native scanner preserved (best of both worlds)
- ✅ Seamless authentication (JWT → Session cookie bridge)
- ✅ Consistent UX across web and mobile

#### Performance Improvements
- **Smaller APK**: Removed thousands of lines of UI code
- **Faster Builds**: Less code to compile
- **Efficient Rendering**: CSS-only animations and transitions
- **Hardware Acceleration**: Using transform for animations

### Migration Guide

#### For Users
No action required. The app will automatically update to the new architecture. Your data and settings are preserved.

#### For Developers
If you've been developing custom features:
1. All UI changes should now be made in the web app (`backend/src/templates/user/`)
2. Mobile app only handles authentication and scanner
3. Use the JavaScript bridge for native-to-web communication
4. Test in both web browser and mobile WebView

### Known Issues
- None at this time

### Upgrade Notes
- The mobile app will feel more responsive due to reduced code size
- All features remain accessible through the WebView
- Scanner functionality is unchanged

---

## [beta-v0.0.2] - 2025-10-09

### Added
- **Admin Web Panel**: Comprehensive web-based admin interface
  - User management (create, view, delete users)
  - Admin privilege management
  - Registration toggle
  - System statistics dashboard
  - Cookie-based authentication
- **Admin Documentation**: Detailed guides for admin panel usage
- **Security Enhancements**: HTTPOnly cookies, session management

### Changed
- Updated README with admin panel information
- Improved API documentation

### Technical Details
- Added Jinja2 templating engine
- Added itsdangerous for secure session tokens
- Implemented cookie-based admin authentication
- Created responsive admin UI with modern design

---

## [beta-v0.0.1] - Initial Release

### Added
- **Mobile App**: React Native app for iOS and Android
  - Barcode scanning for adding books
  - Library management
  - Wishlist functionality
  - Collections/series detection
  - Dark mode support
- **Backend API**: FastAPI-based REST API
  - User authentication (JWT)
  - Book management
  - Google Books API integration
  - PostgreSQL database
- **Docker Support**: Docker Compose setup for easy deployment
- **CI/CD**: GitHub Actions for automated builds
  - Docker image builds
  - Android APK builds

### Features
- Barcode scanning to add books instantly
- Automatic series detection
- Personal notes for each book
- Reading status tracking
- Wishlist management
- Dark mode support

---

**Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.

