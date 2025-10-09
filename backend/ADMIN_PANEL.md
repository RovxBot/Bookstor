# Bookstor Admin Panel

The Bookstor admin panel provides a web-based interface for managing users and application settings.

## Features

- **User Management**: Create, view, and manage users
- **Admin Privileges**: Grant or revoke admin access
- **Registration Control**: Enable or disable new user registration
- **Dashboard**: View system statistics and quick actions
- **Secure Authentication**: Cookie-based session management for admin users

## Accessing the Admin Panel

1. Start the backend server:
   ```bash
   docker-compose up
   ```

2. Navigate to: `http://localhost:8000/admin/login`

3. Login with an admin account:
   - The first user created is automatically an admin
   - Use the `/api/auth/register` endpoint to create the first user
   - Or use the admin panel to create additional users

## First Time Setup

If no users exist yet:

1. Create the first user via API:
   ```bash
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "YourSecurePassword123"}'
   ```

2. The first user is automatically granted admin privileges

3. Login to the admin panel at `http://localhost:8000/admin/login`

## Admin Panel Pages

### Dashboard (`/admin/dashboard`)
- View system statistics (users, books, admins)
- Check registration status
- Quick access to common tasks

### User Management (`/admin/users`)
- View all users and their book counts
- Create new users
- Grant or revoke admin privileges
- Delete users (except yourself)

### Settings (`/admin/settings`)
- Toggle user registration on/off
- View system information
- Access API documentation

## Security Features

- Admin-only access (requires `is_admin = true`)
- Secure cookie-based sessions (7-day expiry)
- HTTPOnly cookies to prevent XSS attacks
- Password validation for new users
- Protection against self-deletion and self-demotion

## API Endpoints

The admin panel uses these API endpoints:

- `POST /admin/api/users` - Create a new user
- `PATCH /admin/api/users/{user_id}/admin` - Toggle admin status
- `DELETE /admin/api/users/{user_id}` - Delete a user
- `POST /admin/api/settings/registration` - Toggle registration

## Notes

- Registration is automatically disabled after the first user is created
- Admins can re-enable registration from the Settings page
- All admin actions are performed via secure API calls
- The admin panel is separate from the mobile app authentication

