"""
Migration script to normalise existing series names in the database
Run this once to fix existing data
"""
import sys
sys.path.insert(0, '/app')

from src.database import SessionLocal
from src.models import Book
from src.services.api_integration_manager import api_integration_manager

def main():
    db = SessionLocal()
    
    try:
        # Get all books with series names
        books_with_series = db.query(Book).filter(Book.series_name.isnot(None)).all()
        
        print(f"\nFound {len(books_with_series)} books with series names")
        print("="*80)
        
        updated_count = 0
        changes = {}
        
        for book in books_with_series:
            original_name = book.series_name
            normalised_name = api_integration_manager.normalise_series_name(original_name)
            
            if normalised_name != original_name:
                # Track the change
                if original_name not in changes:
                    changes[original_name] = normalised_name
                
                # Update the book
                book.series_name = normalised_name
                updated_count += 1
        
        # Show what will be changed
        if changes:
            print(f"\nChanges to be made ({len(changes)} unique series names):")
            print("-"*80)
            for old, new in sorted(changes.items()):
                count = sum(1 for b in books_with_series if b.series_name == new)
                print(f"  '{old}' -> '{new}' ({count} books)")
            
            # Commit changes
            db.commit()
            print(f"\n✓ Successfully updated {updated_count} books")
        else:
            print("\n✓ No changes needed - all series names are already normalised")
        
        # Show final series grouping
        print("\n" + "="*80)
        print("Final series grouping:")
        print("-"*80)
        
        series_counts = {}
        for book in db.query(Book).filter(Book.series_name.isnot(None)).all():
            series_name = book.series_name
            if series_name not in series_counts:
                series_counts[series_name] = 0
            series_counts[series_name] += 1
        
        for series_name, count in sorted(series_counts.items()):
            print(f"  {series_name}: {count} books")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

