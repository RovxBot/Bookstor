# Admin Panel Setup Guide

## Quick Start

### 1. Start the Backend

```bash
# Start with Docker (recommended)
docker-compose up -d

# Or rebuild if you've made changes
docker-compose up -d --build
```

### 2. Create First Admin User

The first user created automatically becomes an admin:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePassword123!"
  }'
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### 3. Access Admin Panel

Open your browser and navigate to:
```
http://localhost:8000/admin/login
```

Login with the credentials you just created.

## Admin Panel Features

### Dashboard (`/admin/dashboard`)
- View total users, books, and admins
- Check registration status
- Quick links to common tasks
- System information

### User Management (`/admin/users`)
- View all users with their book counts
- Create new users (with or without admin privileges)
- Grant or revoke admin status
- Delete users (protection against self-deletion)

### Settings (`/admin/settings`)
- Toggle user registration on/off
- View system information
- Access API documentation
- View available endpoints

## Security Features

✅ **Admin-Only Access**: Only users with `is_admin = true` can access the panel

✅ **Secure Sessions**: HTTPOnly cookies with 7-day expiry

✅ **Password Validation**: Enforced strong password requirements

✅ **Self-Protection**: Cannot delete yourself or remove your own admin status

✅ **Automatic Registration Control**: Registration is disabled after first user

## Troubleshooting

### Cannot Access Admin Panel

1. **Check if backend is running:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

2. **Check logs:**
   ```bash
   docker-compose logs -f backend
   ```

3. **Verify user is admin:**
   ```bash
   # Check in database
   docker-compose exec db psql -U bookstor -d bookstor -c "SELECT id, email, is_admin FROM users;"
   ```

### Static Files Not Loading

If CSS/JS files aren't loading:

1. **Check static directory exists:**
   ```bash
   ls -la backend/src/static/
   ```

2. **Rebuild Docker image:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Login Issues

1. **Verify credentials are correct**
2. **Check user has admin privileges**
3. **Clear browser cookies and try again**
4. **Check backend logs for errors**

## API Endpoints

The admin panel uses these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/login` | Login page |
| POST | `/admin/login` | Process login |
| GET | `/admin/logout` | Logout |
| GET | `/admin/dashboard` | Dashboard page |
| GET | `/admin/users` | User management page |
| GET | `/admin/settings` | Settings page |
| POST | `/admin/api/users` | Create user |
| PATCH | `/admin/api/users/{id}/admin` | Toggle admin status |
| DELETE | `/admin/api/users/{id}` | Delete user |
| POST | `/admin/api/settings/registration` | Toggle registration |

## Development

### Local Development (without Docker)

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up database:**
   ```bash
   # Start PostgreSQL (or use Docker for just the DB)
   docker-compose up -d db
   ```

3. **Run backend:**
   ```bash
   cd backend
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access admin panel:**
   ```
   http://localhost:8000/admin/login
   ```

### File Structure

```
backend/
├── src/
│   ├── routes/
│   │   └── admin.py          # Admin routes and API endpoints
│   ├── static/
│   │   ├── admin.css         # Admin panel styles
│   │   └── admin.js          # Admin panel JavaScript
│   ├── templates/
│   │   └── admin/
│   │       ├── base.html     # Base template
│   │       ├── login.html    # Login page
│   │       ├── dashboard.html # Dashboard
│   │       ├── users.html    # User management
│   │       └── settings.html # Settings
│   └── main.py               # Updated with admin routes
└── requirements.txt          # Updated with jinja2, itsdangerous
```

## Next Steps

After setting up the admin panel:

1. ✅ Create your admin account
2. ✅ Login to the admin panel
3. ✅ Create additional users if needed
4. ✅ Configure registration settings
5. ✅ Set up the mobile app to connect to your server

For mobile app setup, see the main [README.md](README.md).

## Support

For issues or questions:
- Check the [backend/ADMIN_PANEL.md](backend/ADMIN_PANEL.md) for detailed documentation
- Review the main [README.md](README.md) for general setup
- Open an issue on GitHub

