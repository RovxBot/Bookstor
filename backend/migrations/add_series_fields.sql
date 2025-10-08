-- Add series-related fields to books table
ALTER TABLE books ADD COLUMN IF NOT EXISTS subtitle VARCHAR;
ALTER TABLE books ADD COLUMN IF NOT EXISTS series_name VARCHAR;
ALTER TABLE books ADD COLUMN IF NOT EXISTS series_position VARCHAR;

-- Create index on series_name for faster collection queries
CREATE INDEX IF NOT EXISTS idx_books_series_name ON books(series_name);

