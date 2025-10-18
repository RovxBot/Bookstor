# Bookstor

[![Build Docker Image](https://github.com/RovxBot/Bookstor/actions/workflows/build-docker.yml/badge.svg)](https://github.com/RovxBot/Bookstor/actions/workflows/build-docker.yml)
[![Build Android APK](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml/badge.svg)](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/RovxBot/Bookstor/pkgs/container/bookstor)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENCE)

Personal library management system with barcode scanning, automatic series detection, and wishlist management.

## Latest Releases

- **Version**: `v0.0.3` (WebView Architecture)
- **Docker Image**: `ghcr.io/rovxbot/bookstor:latest`
- **Android APK**: [Download from Releases](https://github.com/RovxBot/Bookstor/releases)

## Features

### Web App (Desktop & Mobile)
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile
- **Library Management**: Organise your book collection with reading status
- **Wishlist**: Track books you want to read
- **Collections**: Automatic series detection and grouping
- **Search & Add**: Search Google Books and add to your library
- **Dark Mode**: Full dark mode support with consistent theming
- **Book Details**: View detailed information, add notes, track progress

### Mobile App (Android)
- **WebView-Based**: Lightweight wrapper around the web app
- **Native Barcode Scanner**: Fast barcode scanning to add books instantly
- **Seamless Authentication**: Automatic login synchronisation
- **Offline-Ready**: Web app cached for offline viewing
- **Small APK Size**: ~90% smaller than previous version

### Admin Web Panel
- User management (create, view, delete users)
- Grant or revoke admin privileges
- Toggle user registration on/off
- System statistics dashboard
- Secure cookie-based authentication

## Installation

### Server Setup

**Current Version**: `latest` (automatically built from main branch)

1. **Pull the Docker image:**
   ```bash
   docker pull ghcr.io/rovxbot/bookstor:latest
   ```

   Or use a specific version:
   ```bash
   # Use a specific commit
   docker pull ghcr.io/rovxbot/bookstor:main-abc123

   # Use a tagged release
   docker pull ghcr.io/rovxbot/bookstor:v1.0.0
   ```

2. **Create environment file:**
   ```bash
   # Copy example file
   cp .env.example .env

   # Generate a secure SECRET_KEY (REQUIRED)
   python -c 'import secrets; print(secrets.token_urlsafe(32))'
   # Or use: openssl rand -base64 32

   # Edit .env and add your SECRET_KEY
   nano .env
   ```

   **Important:** The `SECRET_KEY` is required and must be at least 32 characters. The application will not start without it.

3. **Start the server:**
   ```bash
   docker-compose up -d
   ```

   The server will be available at `http://localhost:8000`

### Mobile App Installation

#### Android

**Latest Build**: Automatically built from main branch via GitHub Actions

**What's New in v0.0.4:**
- Fixed mobile app login redirect issue
- Improved WebView URL handling
- Enhanced session management
- Bug fixes and stability improvements

1. **Download the APK:**
   - Go to [Releases](https://github.com/RovxBot/Bookstor/releases)
   - Or download from [Actions Artifacts](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml)

2. **Install on your device:**
   - Enable "Install from Unknown Sources" in Android settings
   - Open the downloaded APK file
   - Follow the installation prompts

3. **Configure the app:**
   - Open Bookstor
   - Login or register an account
   - The app will automatically connect to your server
   - Use the scanner button to add books via barcode

#### iOS
1. Download from the App Store (Coming soon. Maybe.)

### Web App Access

You can also access Bookstor directly in your web browser:
- **Desktop**: Navigate to `http://localhost:8000/app/library`
- **Mobile**: Navigate to `http://YOUR_SERVER_IP:8000/app/library`
- **Features**: Full library management, search, collections, and settings

## Version Information

### Check Docker Image Version

```bash
# List all available tags
docker images ghcr.io/rovxbot/bookstor

# Check image details
docker inspect ghcr.io/rovxbot/bookstor:latest | grep -A 5 Labels
```

### Check Android App Version

1. Open Bookstor app
2. Go to Settings
3. Scroll to bottom to see version information

### View Build Status

- **Docker Builds**: [View workflow runs](https://github.com/RovxBot/Bookstor/actions/workflows/build-docker.yml)
- **Android Builds**: [View workflow runs](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml)

## Configuration

### Server Configuration

Edit your `.env` file:

```env
# Required
DATABASE_URL=postgresql://bookstor:bookstor_password@db:5432/bookstor
SECRET_KEY=your-generated-secret-key-here

# Optional - Get from https://console.cloud.google.com/
GOOGLE_BOOKS_API_KEY=your-api-key

# CORS Configuration (optional)
# Use "*" for development (credentials disabled automatically)
# In production, specify exact origins:
# CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ORIGINS=*
```

**Security Notes:**
- `SECRET_KEY` must be at least 32 characters and cryptographically secure
- `CORS_ORIGINS=*` is convenient for development but disables credentials
- In production, always specify exact allowed origins for security

### Mobile App Configuration

**v0.0.3 Note**: The mobile app now uses a WebView to display the web interface. Configuration is done through the native login screen.

1. Open the app
2. Enter your server URL on the login screen:
   - Local network: `http://192.168.1.XXX:8000/api`
   - Public server: `https://your-domain.com/api`
3. Login or register an account
4. The app will automatically load the web interface

## Usage

### Web App

Access the web app at `http://localhost:8000/app/library`

**Features:**
- **Library**: View and filter your book collection by reading status
- **Wishlist**: Track books you want to read
- **Collections**: Browse automatically detected book series
- **Search**: Search Google Books and add to your library
- **Settings**: Manage your account and preferences

**Mobile Web:**
- Responsive design optimised for mobile devices
- Bottom navigation for easy access
- Touch-friendly interface
- Dark mode support

### Admin Panel

Access the admin panel at `http://localhost:8000/admin/login`

**First Time Setup:**
1. Create the first user via API (automatically becomes admin):
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "YourSecurePassword123"}'
   ```

2. Login to admin panel with your credentials

**Admin Features:**
- **Dashboard**: View system statistics and quick actions
- **User Management**: Create users, manage admin privileges, delete users
- **Settings**: Toggle registration, view API documentation

See [backend/ADMIN_PANEL.md](backend/ADMIN_PANEL.md) for detailed admin panel documentation.

### Mobile App

**v0.0.3 Architecture:**
The mobile app is now a lightweight WebView wrapper that displays the web interface with a native barcode scanner.

1. **Login** - Login or register through the native login screen
2. **Browse Library** - View your collection in the WebView interface
3. **Scan Books** - Tap the floating scanner button to scan barcodes
4. **Manage Collection** - All web features available in the app
5. **Seamless Experience** - Automatic authentication and theme synchronisation

## Architecture

### v0.0.3 WebView Architecture

Bookstor v0.0.3 introduces a major architectural change for the mobile app:

**Previous Architecture (v0.0.2):**
- Fully native React Native UI
- Duplicate code for web and mobile
- 10 screens, ~5,000 lines of mobile UI code
- Larger APK size (~15-20 MB)

**New Architecture (v0.0.3):**
- WebView-based mobile app
- Single UI codebase (web app)
- 4 screens, ~500 lines of mobile code (90% reduction!)
- Smaller APK size (~2-3 MB)
- Native barcode scanner preserved

**Benefits:**
- ✅ **Single Source of Truth**: All UI changes in one place
- ✅ **Faster Development**: New features only need web implementation
- ✅ **Consistent UX**: Identical experience on web and mobile
- ✅ **Smaller APK**: 90% reduction in mobile code
- ✅ **Easier Maintenance**: No duplicate features to maintain
- ✅ **Native Scanner**: Best of both worlds - web UI + native scanner

**How It Works:**
1. Mobile app loads web interface in a WebView
2. Native login screen handles authentication
3. JWT token converted to session cookie for WebView
4. Floating action button triggers native scanner
5. Scanner sends ISBN to WebView via JavaScript injection
6. Web app processes the ISBN and updates the library

## Troubleshooting

### Cannot connect to server

**From mobile app:**
1. Ensure server is running: `docker-compose ps`
2. Check server URL in app Settings
3. Use your computer's local IP address (not localhost)
4. Ensure firewall allows connections on port 8000

**Test connection:**
```bash
curl http://YOUR_SERVER_IP:8000/health
```

### Server won't start

```bash
# View logs
docker-compose logs -f backend

# Restart services
docker-compose restart
```

### App crashes or won't scan

1. Grant camera permissions when prompted
2. Ensure good lighting for barcode scanning
3. Try reinstalling the app

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/yourusername/bookstor/issues)
- Check existing issues for solutions

## Licence

MIT Licence - see [LICENCE](LICENCE) file for details.

---

**Made with ❤️ for book lovers**
