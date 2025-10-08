# Bookstor

[![Build Docker Image](https://github.com/RovxBot/Bookstor/actions/workflows/build-docker.yml/badge.svg)](https://github.com/RovxBot/Bookstor/actions/workflows/build-docker.yml)
[![Build Android APK](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml/badge.svg)](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/RovxBot/Bookstor/pkgs/container/bookstor)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENCE)

Personal library management system with barcode scanning, automatic series detection, and wishlist management.

## Latest Releases

- **Docker Image**: `ghcr.io/rovxbot/bookstor:latest`
- **Android APK**: [Download from Releases](https://github.com/RovxBot/Bookstor/releases)

## Features

- Barcode scanning to add books instantly
- Manage your book collection
- Wishlist for books you want to read
- Automatic series detection and collections
- Dark mode support
- Personal notes for each book

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
   # Create .env file
   cat > .env << 'ENVEOF'
   DATABASE_URL=postgresql://bookstor:bookstor@db:5432/bookstor
   SECRET_KEY=$(openssl rand -hex 32)
   GOOGLE_BOOKS_API_KEY=your_api_key_here
   ENVEOF
   ```

3. **Start the server:**
   ```bash
   docker-compose up -d
   ```

   The server will be available at `http://localhost:8000`

### Mobile App Installation

#### Android

**Latest Build**: Automatically built from main branch via GitHub Actions

1. **Download the APK:**
   - Go to [Releases](https://github.com/RovxBot/Bookstor/releases)
   - Or download from [Actions Artifacts](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml)

2. **Install on your device:**
   - Enable "Install from Unknown Sources" in Android settings
   - Open the downloaded APK file
   - Follow the installation prompts

3. **Configure the app:**
   - Open Bookstor
   - Go to Settings
   - Enter your server URL

#### iOS
1. Download from the App Store (Coming soon. Maybe.)

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
DATABASE_URL=postgresql://bookstor:bookstor@db:5432/bookstor
SECRET_KEY=your-secret-key-here

# Optional - Get from https://console.cloud.google.com/
GOOGLE_BOOKS_API_KEY=your-api-key
```

### Mobile App Configuration

1. Open the app
2. Go to Settings
3. Enter your server URL:
   - Local network: `http://192.168.1.XXX:8000/api`
   - Public server: `https://your-domain.com/api`

## Usage

1. **Register an account** - Create your account on first launch
2. **Scan books** - Use the barcode scanner to add books
3. **Manage library** - View and organise your collection
4. **Create wishlist** - Add books you want to read
5. **Discover series** - Automatically grouped into collections

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
