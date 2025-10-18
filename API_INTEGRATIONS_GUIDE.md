# API Integrations Guide

## Overview

Bookstor now supports dynamic API integrations for book metadata fetching. You can add, configure, and manage multiple book APIs through the admin portal without modifying code.

## Features

- **Dynamic API Management**: Add/remove book APIs through the admin interface
- **Priority-Based Querying**: Set priority to control which APIs are queried first
- **Data Merging**: Automatically merges results from multiple APIs to get the most complete metadata
- **Enable/Disable**: Toggle APIs on/off without deleting them
- **Custom APIs**: Add your own book APIs with custom endpoints

## Accessing API Integrations

1. Log in to the admin portal at `http://localhost:8000/admin`
2. Navigate to **API Integrations** from the sidebar or dashboard
3. View, add, edit, or delete API integrations

## Pre-Configured APIs

### Open Library
- **Priority**: 1 (checked first)
- **Base URL**: https://openlibrary.org
- **API Key Required**: No
- **Status**: Enabled by default

### Google Books API
- **Priority**: 2 (checked second)
- **Base URL**: https://www.googleapis.com/books/v1/volumes
- **API Key Required**: Optional (recommended for higher rate limits)
- **Status**: Enabled by default

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

#### Google Books API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "Books API"
4. Create credentials (API Key)
5. Copy the API key and paste it into Bookstor

#### Other APIs
Refer to the specific API's documentation for obtaining API keys.

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
- Goodreads (Priority 3)

Bookstor will:
1. Query Open Library first
2. Query Google Books second
3. Query Goodreads third
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

## Custom API Integration

You can add custom book APIs that follow common patterns. Bookstor will attempt to parse responses from:

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

1. **Set Priorities Wisely**: Put your most reliable/comprehensive API at Priority 1
2. **Use API Keys**: When available, use API keys for better rate limits and reliability
3. **Test New APIs**: Add new APIs with low priority first, then adjust after testing
4. **Keep Backups**: Have multiple APIs enabled in case one goes down
5. **Monitor Usage**: Check backend logs occasionally to ensure APIs are working correctly

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

