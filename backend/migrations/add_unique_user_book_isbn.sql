-- Ensure unique (user_id, isbn) to prevent duplicates (idempotent)
DO $$
BEGIN
	IF NOT EXISTS (
		SELECT 1 FROM pg_constraint WHERE conname = 'uq_books_user_isbn'
	) THEN
		ALTER TABLE books ADD CONSTRAINT uq_books_user_isbn UNIQUE (user_id, isbn);
	END IF;
END$$;

-- Helpful composite index for queries by user and added_at
CREATE INDEX IF NOT EXISTS idx_books_user_added_at ON books(user_id, added_at DESC);
