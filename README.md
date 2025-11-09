# Bookstor

[![Build Docker Image](https://github.com/RovxBot/Bookstor/actions/workflows/build-docker.yml/badge.svg)](https://github.com/RovxBot/Bookstor/actions/workflows/build-docker.yml)
[![Build Android APK](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml/badge.svg)](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml)
[![Docker Image](https://img.shields.io/badge/docker-ghcr.io-blue?logo=docker)](https://github.com/RovxBot/Bookstor/pkgs/container/bookstor)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENCE)

A self-hosted personal library management system with barcode scanning, automatic metadata fetching, and a beautiful interface.

**Current Version**: `v0.0.6` | [View Changelog](CHANGELOG.md)

## What is Bookstor?

Bookstor helps you manage your personal book collection with ease. Scan barcodes with your phone, automatically fetch book details from multiple sources, organise your library by reading status, track series, and manage your wishlist.

**Key Features:**
- **Mobile barcode scanning** - Add books instantly by scanning ISBN barcodes
- **Multi-source metadata** - Automatically fetches book details from Google Books, Open Library, and Hardcover
- **Smart organisation** - Automatic series detection and grouping
- **Beautiful UI** - Modern interface with horizontal scrolling and grid views
- **Advanced search** - Real-time filtering by title, author, category, and reading status
- **Wishlist management** - Track books you want to read with purchase workflow
- **Dark mode** - Full dark mode support
- **Self-hosted** - Your data stays on your server

## How It Works

1. **Deploy the server** using Docker on your home server or cloud provider
2. **Create your first user** via the API or admin panel
3. **Install the mobile app** on your Android device
4. **Scan book barcodes** to automatically add books to your library
5. **Browse and organise** your collection with reading statuses and series
6. **Track your wishlist** and mark books as purchased when you buy them

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- A server or computer to host the application
- Python 3.11+ (optional for generating secrets locally)
- (Optional) Android device for mobile app

## Deployment

### 1. Deploy the Server

#### Option A: Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/RovxBot/Bookstor.git
cd Bookstor

# Create environment file
cp backend/.env.example backend/.env

# Generate a secure SECRET_KEY (REQUIRED)
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Or: openssl rand -base64 32

# Edit .env and add your SECRET_KEY
nano backend/.env

# Start the server
docker-compose up -d
```

The server will be available at `http://localhost:8000`

#### Option B: Using Pre-built Docker Image

```bash
# Pull the latest image
docker pull ghcr.io/rovxbot/bookstor:latest

# Create your docker-compose.yml and .env files
# Then start the server
docker-compose up -d
```

**Important:** The `SECRET_KEY` environment variable is required and must be at least 32 characters. The application will not start without it.

### 2. Seed API Integrations (Optional but Recommended)

To enable multi-source metadata lookups immediately, seed default integrations (Google Books & Open Library):

```bash
docker compose exec backend python seed_integrations.py
```

You can then add/adjust priorities or add Hardcover via the Admin Panel.

### 3. Create Your First User

The first user you create automatically becomes an admin.

#### Option A: Via API
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "YourSecurePassword123!"
  }'
```

#### Option B: Via Admin Panel
1. Navigate to `http://localhost:8000/admin/login`
2. Click "Create First Admin User"
3. Fill in your email and password
4. Login with your new credentials

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### 4. Get the Mobile App

#### Android

1. **Download the APK:**
   - [Latest Release](https://github.com/RovxBot/Bookstor/releases)
   - Or [GitHub Actions Artifacts](https://github.com/RovxBot/Bookstor/actions/workflows/build-apk-local.yml)

2. **Install on your device:**
   - Enable "Install from Unknown Sources" in Android settings
   - Open the downloaded APK file
   - Follow the installation prompts

3. **Connect to your server:**
   - Open Bookstor app
   - Enter your server URL (e.g., `http://192.168.1.100:8000/api`)
   - Login with your credentials
   - Start scanning books!

#### iOS
- Coming soon (maybe)

#### Web Browser
- You can also use Bookstor directly in your web browser
- Navigate to `http://localhost:8000/app/library` (or your server IP)
- Full functionality available on desktop and mobile browsers

## Using Bookstor

### Web Interface

Access the web app at `http://localhost:8000/app/library` (or your server IP)

**Main Features:**


1. **Library** - View your book collection organised by reading status
   - Currently Reading
   - Want to Read
   - Finished
   - Search and filter in real-time

2. **Wishlist** - Track books you want to buy
   - Add books to wishlist
   - Mark as "Purchased" to move to library

3. **Collections** - Browse automatically detected book series
   - See all books in a series
   - Track missing books
   - Add missing books to wishlist

4. **Search** - Find and add new books
   - Search by title, author, or ISBN
   - Automatically fetches metadata from multiple sources
   - Add directly to library or wishlist

5. **Book Details** - View and edit book information
   - Cover image, title, author, description
   - Reading status and progress
   - Notes and personal ratings
   - Refresh metadata from APIs

### Mobile App

**Barcode Scanning:**

1. Tap the floating scanner button (camera icon)
2. Point camera at book's ISBN barcode
3. Choose to add to Library or Wishlist
4. Book details automatically fetched and added

**All Web Features:**
- The mobile app uses a WebView to display the full web interface
- All features available on mobile as on desktop
- Seamless authentication and synchronisation

### Admin Panel

Access the admin panel at `http://localhost:8000/admin/login`

**Features:**

1. **Dashboard** - System overview
   - Total users, books, and admins
   - Registration status
   - Quick actions

2. **User Management** - Manage users
   - Create new users
   - Grant/revoke admin privileges
   - Delete users
   - View user book counts

3. **API Integrations** - Configure book metadata sources
   - Add API integrations (Google Books, Open Library, Hardcover)
   - Set priority order for data fetching
   - Enable/disable integrations
   - Configure API keys

4. **Settings** - System configuration
   - Toggle user registration on/off
   - View API documentation
   - System information

See [ADMIN_SETUP.md](ADMIN_SETUP.md) for detailed admin panel documentation.

## Configuration

### Environment Variables

Edit `backend/.env`:

```env
# Required
DATABASE_URL=postgresql://bookstor:bookstor_password@db:5432/bookstor
SECRET_KEY=your-generated-secret-key-here  # Must be 32+ characters

# Optional API Keys (These can be added in the GUI)
GOOGLE_BOOKS_API_KEY=your-google-books-api-key

# CORS (optional)
CORS_ORIGINS=*  # Use specific origins in production

# Logging
LOG_LEVEL=INFO
```

### API Integrations

Bookstor can fetch book metadata from multiple sources:

1. **Google Books** - No API required, but recommended for better results (free from Google Cloud Console)
2. **Open Library** - No API key required
3. **Hardcover** - Requires API key (free from hardcover.app)

Configure these in the Admin Panel under "API Integrations".

### Database Constraints

Bookstor enforces uniqueness for `(user_id, isbn)` at the database level to prevent duplicate entries of the same ISBN for a user. If you are upgrading from an older version you can apply the migration manually:

```bash
docker compose exec backend psql $DATABASE_URL -f migrations/add_unique_user_book_isbn.sql
```

### Running Tests

Tests now run inside the backend container with `pytest`:

```bash
docker compose exec backend python -m pytest -q
```

Key test areas:
- ISBN checksum validation & normalization (`test_isbn_utils.py`)
- External integration probes (Google/Open Library)
- Concurrency safety in integration manager

### Concurrency & Data Merging (v0.0.6)

As of `v0.0.6`, external API calls for ISBN and title searches execute concurrently using `asyncio.gather`, reducing latency when multiple integrations are enabled. Results are merged only when ISBNs match after normalization (supports ISBN-10 → ISBN-13 conversion). Non-matching responses are discarded to maintain data integrity.

### Security Enhancements

- Strict ISBN validation on add-by-ISBN routes
- Unique constraint to avoid duplicates
- Centralized logging configuration (`logging_config.py`)
- Enforced secure `SECRET_KEY` validation via Pydantic

### Caching (Optional Redis)

Book metadata lookups by ISBN can be cached in Redis to reduce repeated external API calls. Enable caching by setting `REDIS_URL` in `.env` (default expected format: `redis://redis:6379/0`). If Redis is unavailable or not configured, the application operates normally without caching.

Current cached objects:
- Merged ISBN lookup results (safe merge payload)

Current cached objects:

- Merged ISBN lookup results (safe merge payload)
Planned future cached objects:
- Series gap computations (missing books per series per user)

Planned future cached objects:

- Series gap computations (missing books per series per user)
Disable caching simply by omitting `REDIS_URL`.



## Troubleshooting

### Server Issues

#### Server won't start:
```bash
# Check logs
docker-compose logs -f backend

#### App crashes or login fails
# Verify SECRET_KEY is set in .env
cat backend/.env | grep SECRET_KEY

# Restart services
docker-compose restart
```

#### Cannot access web interface:
1. Verify server is running: `docker-compose ps`
2. Check firewall allows port 8000
3. Try accessing from `http://localhost:8000`

### Mobile App Issues

#### Cannot connect to server:
1. Ensure server is running: `docker-compose ps`
2. Use your computer's local IP address (not localhost)
   - Find IP: `ip addr` (Linux) or `ipconfig` (Windows)
   - Example: `http://192.168.1.100:8000/api`
3. Ensure firewall allows connections on port 8000
4. Test connection: `curl http://YOUR_SERVER_IP:8000/`

#### Barcode scanner not working:
1. Grant camera permissions when prompted
2. Ensure good lighting for scanning
3. Hold barcode steady and at proper distance
4. Try reinstalling the app

#### App crashes or login fails:
1. Check server URL is correct (must end with `/api`)
2. Verify server is accessible from your device
3. Clear app data and try again
4. Check server logs for errors

## Documentation

- [CHANGELOG.md](CHANGELOG.md) - Version history and technical changes
- [ADMIN_SETUP.md](ADMIN_SETUP.md) - Detailed admin panel guide
- [API_INTEGRATIONS_GUIDE.md](API_INTEGRATIONS_GUIDE.md) - API integration documentation

## Support

- **Issues**: [GitHub Issues](https://github.com/RovxBot/Bookstor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RovxBot/Bookstor/discussions)

## Licence

MIT Licence - see [LICENCE](LICENCE) file for details.

---

**Made with ❤️ for book lovers**
