# Bookstor

Personal library management system with barcode scanning, automatic series detection, and wishlist management.

## Features

- Barcode scanning to add books instantly
- Manage your book collection
- Wishlist for books you want to read
- Automatic series detection and collections
- Dark mode support
- Personal notes for each book

## Installation

### Server Setup

1. **Pull the Docker image:**
   ```bash
   docker pull ghcr.io/rovxbot/bookstor:latest
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
1. Download the APK from [Releases](https://github.com/rovxbot/bookstor/releases)
2. Install the APK on your Android device
3. Open the app and configure the server URL in Settings

#### iOS
1. Download from the App Store (coming soon. Maybe.)

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
