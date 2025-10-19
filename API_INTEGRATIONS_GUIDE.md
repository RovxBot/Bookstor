# API Integrations Guide

## Overview

Bookstor supports dynamic API integrations for book metadata fetching. You can add, configure, and manage multiple book APIs through the admin portal without modifying code.

**Currently Supported APIs**: Bookstor has been tested and confirmed to work with **3 API endpoints**:
1. **Open Library** (no API key required)
2. **Google Books** (optional API key for higher rate limits)
3. **Hardcover** (API key required)

While the system supports adding custom APIs, only these three have been fully tested and verified to work correctly.

## Features

- **Dynamic API Management**: Add/remove book APIs through the admin interface
- **Priority-Based Querying**: Set priority to control which APIs are queried first
- **Data Merging**: Automatically merges results from multiple APIs to get the most complete metadata
- **Enable/Disable**: Toggle APIs on/off without deleting them
- **Tested APIs**: Three fully tested and working API integrations

## Accessing API Integrations

1. Log in to the admin portal at `http://localhost:8000/admin`
2. Navigate to **API Integrations** from the sidebar or dashboard
3. View, add, edit, or delete API integrations

## Tested and Supported APIs

### 1. Open Library
- **Priority**: 1 (checked first)
- **Base URL**: `https://openlibrary.org`
- **API Key Required**: No
- **Status**: Enabled by default
- **Coverage**: Good for older and classic books

### 2. Google Books API
- **Priority**: 2 (checked second)
- **Base URL**: `https://www.googleapis.com/books/v1/volumes`
- **API Key Required**: Optional (recommended for higher rate limits)
- **Status**: Enabled by default
- **Coverage**: Excellent for modern books and comprehensive metadata

### 3. Hardcover
- **Priority**: 3 (checked third)
- **Base URL**: `https://api.hardcover.app/v1/graphql`
- **API Key Required**: Yes (free from hardcover.app)
- **Status**: Must be added manually via admin panel
- **Coverage**: Best for series information and community-driven data
- **Special**: Uses GraphQL API

## Adding a New API Integration

### Step 1: Click "Add Integration"

Click the **Add Integration** button on the API Integrations page.

### Step 2: Fill in the Form

- **Name**: Internal identifier (lowercase, no spaces, e.g., `goodreads`, `librarything`)
- **Display Name**: Human-readable name (e.g., "Goodreads API")
- **Description**: Brief description of the API
- **Base URL**: The API's base endpoint URL
- **API Key**: Your API key (if required)
- **Priority**: Lower numbers = higher priority (1 is checked first)
- **Requires API Key**: Check if this API requires an API key to function

### Step 3: Save

Click **Save** to add the integration. It will be enabled by default.

## Editing an Existing Integration

1. Click the **Edit** button on any integration card
2. Modify the fields as needed
3. Click **Save** to update

## Managing API Keys

### Adding an API Key

1. Edit the integration
2. Enter your API key in the **API Key** field
3. Save the changes

### Security

- API keys are stored in the database
- Only the last 4 characters are displayed in the UI
- Full keys are never shown after saving

### Getting API Keys

#### Google Books API (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Books API"
4. Create credentials (API Key)
5. Copy the API key and paste it into Bookstor

**Note**: Google Books works without an API key but has lower rate limits.

#### Hardcover API (Required)
1. Go to [Hardcover.app](https://hardcover.app/)
2. Create a free account
3. Navigate to Settings → API
4. Generate an API key
5. Add Hardcover integration in Bookstor admin panel:
   - **Name**: `hardcover`
   - **Display Name**: `Hardcover`
   - **Base URL**: `https://api.hardcover.app/v1/graphql`
   - **API Key**: Paste your Hardcover API key
   - **Priority**: 3 (or your preference)
   - **Requires API Key**: Check this box

## Priority System

The priority system determines the order in which APIs are queried:

- **Priority 1**: Checked first
- **Priority 2**: Checked second
- **Priority 3+**: Checked in ascending order

### How It Works

1. When searching for a book by ISBN or title, Bookstor queries all enabled APIs in priority order
2. Results from all APIs are collected
3. Data is merged to create the most complete book record
4. Missing fields from higher-priority APIs are filled in by lower-priority APIs

### Example

If you have:
- Open Library (Priority 1)
- Google Books (Priority 2)
- Hardcover (Priority 3)

Bookstor will:
1. Query Open Library first
2. Query Google Books second
3. Query Hardcover third
4. Merge all results, preferring data from Open Library when available

## Enabling/Disabling APIs

Use the toggle switch on each integration card to enable or disable an API:

- **Enabled** (green): API will be queried for book searches
- **Disabled** (grey): API will be skipped

This is useful for:
- Temporarily disabling an API without deleting it
- Testing different API combinations
- Avoiding rate limits by rotating APIs

## Deleting an Integration

1. Click the **Delete** button on the integration card
2. Confirm the deletion
3. The integration will be permanently removed

**Note**: Deleting an integration does not affect existing book data in your library.

## Custom API Integration (Experimental)

**Warning**: While Bookstor supports adding custom book APIs, only the three APIs listed above (Open Library, Google Books, Hardcover) have been fully tested and verified to work correctly. Custom APIs may require code modifications to work properly.

If you want to experiment with custom APIs, Bookstor will attempt to parse responses that follow common patterns:

### Supported URL Patterns

#### ISBN Search
- `{base_url}/isbn/{isbn}`
- `{base_url}/search?isbn={isbn}`
- `{base_url}/volumes?q=isbn:{isbn}`

#### Title Search
- `{base_url}/search?q={query}&limit={max_results}`
- `{base_url}/volumes?q={query}&maxResults={max_results}`

### Supported Authentication

- **Bearer Token**: `Authorization: Bearer {api_key}`
- **API Key Header**: `X-API-Key: {api_key}`

### Response Format

Bookstor can parse responses that include these common fields:

```json
{
  "title": "Book Title",
  "subtitle": "Book Subtitle",
  "authors": ["Author Name"],
  "description": "Book description",
  "publisher": "Publisher Name",
  "publishedDate": "2024-01-01",
  "pageCount": 300,
  "categories": ["Fiction", "Mystery"],
  "thumbnail": "https://example.com/cover.jpg",
  "isbn": "9781234567890"
}
```

Or nested in `volumeInfo` (Google Books style):

```json
{
  "volumeInfo": {
    "title": "Book Title",
    ...
  }
}
```

Or as an array in `items`, `docs`, or `results`:

```json
{
  "items": [
    {
      "title": "Book Title",
      ...
    }
  ]
}
```

**Note**: Custom APIs may not work without code modifications. For best results, use the three tested APIs listed above.

## How Book Searches Work

### ISBN Lookup

When you scan a barcode or enter an ISBN:

1. Bookstor queries all enabled APIs in priority order
2. Each API is searched for the ISBN
3. Results are collected from all APIs
4. Data is merged:
   - Non-null values are preferred
   - Lists (authors, categories) are combined and deduplicated
   - First result's values are used when multiple APIs provide the same field

### Title Search

When you search by title:

1. Bookstor queries all enabled APIs in priority order
2. Results from all APIs are combined
3. Duplicates are removed based on ISBN or title+author
4. Results are limited to the requested number (default: 10)

### Metadata Refresh

When you click "Refresh Metadata" on a book:

1. If the book has an ISBN, all enabled APIs are queried by ISBN
2. If no ISBN, APIs are queried by title and author
3. Existing book data is updated with new data from APIs
4. Only non-empty fields are updated (existing data is not overwritten with null values)

## Troubleshooting

### API Not Returning Results

1. Check that the API is **Enabled**
2. Verify the **Base URL** is correct
3. If the API requires a key, ensure it's entered correctly
4. Check the API's rate limits and quotas
5. Review backend logs for error messages: `docker compose logs backend --tail 50`

### Incorrect Data

1. Check the **Priority** settings - higher priority APIs take precedence
2. Try disabling other APIs to isolate which one is providing incorrect data
3. Edit the integration to update the Base URL or API key

### Rate Limiting

If you're hitting rate limits:

1. Add an API key (if supported) for higher limits
2. Disable the API temporarily
3. Add alternative APIs and adjust priorities
4. Wait for the rate limit to reset

## Best Practices

1. **Use Tested APIs**: Stick to the three tested APIs (Open Library, Google Books, Hardcover) for best results
2. **Set Priorities Wisely**: Put your most reliable/comprehensive API at Priority 1
3. **Use API Keys**: Add a Google Books API key for higher rate limits, and add Hardcover for best metadata coverage
4. **Keep Multiple APIs Enabled**: Have at least 2-3 APIs enabled in case one goes down or doesn't have data for a specific book
5. **Monitor Usage**: Check backend logs occasionally to ensure APIs are working correctly
6. **Avoid Untested APIs**: Custom APIs may not work without code modifications

## Technical Details

### Database Schema

API integrations are stored in the `api_integrations` table:

```sql
CREATE TABLE api_integrations (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR NOT NULL,
    description TEXT,
    api_key VARCHAR,
    base_url VARCHAR,
    is_enabled BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    requires_key BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Code Integration

The system uses `APIIntegrationManager` which:
- Queries the database for enabled integrations
- Sorts by priority
- Attempts to use existing service classes (Google Books, Open Library)
- Falls back to generic API parsing for custom integrations
- Merges results from multiple sources

### Extending the System

To add native support for a new API (beyond generic parsing):

1. Create a new service class in `backend/src/services/`
2. Implement `search_by_isbn()` and `search_by_title()` methods
3. Add the service to `APIIntegrationManager.service_map` in `api_integration_manager.py`
4. Add the integration through the admin UI

## Support

For issues or questions:
- Check backend logs: `docker compose logs backend --tail 50`
- Review this guide
- Check the API provider's documentation
- Ensure your API keys are valid and have sufficient quota

