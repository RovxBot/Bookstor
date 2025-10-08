"""
Migration script to add registration settings and admin flag
Run this after updating the models
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bookstor:bookstor_password@db:5432/bookstor")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def migrate():
    """Add new columns and table"""
    db = SessionLocal()
    
    try:
        print("Starting migration...")
        
        # Add is_admin column to users table
        print("Adding is_admin column to users table...")
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;
        """))
        
        # Set first user as admin
        print("Setting first user as admin...")
        db.execute(text("""
            UPDATE users 
            SET is_admin = TRUE 
            WHERE id = (SELECT MIN(id) FROM users);
        """))
        
        # Create app_settings table
        print("Creating app_settings table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR UNIQUE NOT NULL,
                value VARCHAR NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Check if any users exist
        result = db.execute(text("SELECT COUNT(*) FROM users")).fetchone()
        user_count = result[0] if result else 0
        
        # If users exist, disable registration by default
        if user_count > 0:
            print(f"Found {user_count} existing users. Disabling registration by default...")
            db.execute(text("""
                INSERT INTO app_settings (key, value, updated_at)
                VALUES ('registration_enabled', 'false', CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO NOTHING;
            """))
        else:
            print("No users found. Registration will remain open for first user.")
        
        db.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

