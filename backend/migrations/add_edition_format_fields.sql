-- Add edition and book_format fields to books table
ALTER TABLE books ADD COLUMN IF NOT EXISTS edition VARCHAR;
ALTER TABLE books ADD COLUMN IF NOT EXISTS book_format VARCHAR;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_books_edition ON books(edition);
CREATE INDEX IF NOT EXISTS idx_books_book_format ON books(book_format);

