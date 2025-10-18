-- Migration: Add API Integrations table
-- Date: 2025-10-18
-- Description: Add table for managing external API integrations (Google Books, Open Library, etc.)

CREATE TABLE IF NOT EXISTS api_integrations (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    display_name VARCHAR NOT NULL,
    description TEXT,
    api_key VARCHAR,
    base_url VARCHAR,
    is_enabled BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    requires_key BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_api_integrations_name ON api_integrations(name);
CREATE INDEX IF NOT EXISTS idx_api_integrations_priority ON api_integrations(priority);
CREATE INDEX IF NOT EXISTS idx_api_integrations_enabled ON api_integrations(is_enabled);

-- Insert default API integrations
INSERT INTO api_integrations (name, display_name, description, base_url, is_enabled, priority, requires_key)
VALUES 
    ('open_library', 'Open Library', 'Free and open book database with extensive metadata', 'https://openlibrary.org', TRUE, 1, FALSE),
    ('google_books', 'Google Books API', 'Google''s comprehensive book database with rich metadata', 'https://www.googleapis.com/books/v1', TRUE, 2, FALSE)
ON CONFLICT (name) DO NOTHING;

