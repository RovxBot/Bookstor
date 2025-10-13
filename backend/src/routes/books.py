from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth
from ..database import get_db
from ..services.google_books import google_books_service
from ..services.openlibrary import openlibrary_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/search", response_model=List[schemas.GoogleBookInfo])
@router.get("/search/", response_model=List[schemas.GoogleBookInfo])
async def search_books(
    q: str = Query(..., description="Search query (title, author, etc.)"),
    max_results: int = Query(10, ge=1, le=40, description="Maximum number of results"),
    current_user: models.User = Depends(auth.get_current_user_flexible)
):
    """Search for books using Google Books API"""
    results = await google_books_service.search_by_title(q, max_results)
    return results


@router.post("/isbn/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
async def add_book_by_isbn(
    isbn_lookup: schemas.ISBNLookup,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Add a book to library by scanning ISBN"""
    # Check if book already exists for this user
    existing_book = db.query(models.Book).filter(
        models.Book.user_id == current_user.id,
        models.Book.isbn == isbn_lookup.isbn
    ).first()
    
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already exists in your library"
        )
    
    # Fetch book info from Google Books API
    book_info = await google_books_service.search_by_isbn(isbn_lookup.isbn)
    
    if not book_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in Google Books database"
        )
    
    # Create book entry
    db_book = models.Book(
        user_id=current_user.id,
        isbn=isbn_lookup.isbn,
        google_books_id=book_info.google_books_id,
        title=book_info.title,
        subtitle=book_info.subtitle,
        authors=", ".join(book_info.authors) if book_info.authors else None,
        description=book_info.description,
        publisher=book_info.publisher,
        published_date=book_info.published_date,
        page_count=book_info.page_count,
        categories=", ".join(book_info.categories) if book_info.categories else None,
        thumbnail=book_info.thumbnail,
        series_name=book_info.series_name,
        series_position=book_info.series_position,
        reading_status=isbn_lookup.reading_status,
        is_wishlist=isbn_lookup.is_wishlist
    )
    
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    return db_book


@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def add_book_manually(
    book: schemas.BookCreate,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Manually add a book (useful for wishlist items without ISBN)"""
    db_book = models.Book(
        user_id=current_user.id,
        **book.model_dump()
    )
    
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    
    return db_book


@router.get("/collections/")
def get_collections(
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Get book collections grouped by series"""
    books = db.query(models.Book).filter(
        models.Book.user_id == current_user.id,
        models.Book.is_wishlist == False
    ).order_by(models.Book.series_name, models.Book.series_position, models.Book.title).all()

    # Group books by series using the series_name field
    collections = {}

    for book in books:
        # Use the series_name field if available
        if book.series_name:
            series_name = book.series_name

            if series_name not in collections:
                collections[series_name] = {
                    'name': series_name,
                    'author': book.authors.split(',')[0].strip() if book.authors else None,
                    'books': []
                }
            collections[series_name]['books'].append(book)

    # Return all collections, even with just 1 book (to help add rest of series to wishlist)
    result = list(collections.values())

    # Sort collections by name
    result.sort(key=lambda x: x['name'])

    return result


@router.get("/collections/{series_name}/missing")
async def get_missing_books(
    series_name: str,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Get missing books from a series that could be added to wishlist"""
    # Get user's books from this series
    user_books = db.query(models.Book).filter(
        models.Book.user_id == current_user.id,
        models.Book.series_name == series_name
    ).all()

    # Get titles of books user already has
    user_book_titles = {book.title for book in user_books}

    # Fetch complete series information from Open Library
    complete_series_books = await openlibrary_service.search_series_books(series_name, limit=50)

    # Find missing books
    missing_books = [
        {
            'title': book['title'],
            'author': book['author'],
            'position': book['position']
        }
        for book in complete_series_books
        if book['title'] not in user_book_titles
    ]

    return {
        "series_name": series_name,
        "total_books": len(complete_series_books),
        "owned_books": len(user_books),
        "missing_books": missing_books
    }


@router.get("/", response_model=List[schemas.Book])
def get_books(
    reading_status: Optional[str] = Query(None, description="Filter by reading status"),
    is_wishlist: Optional[bool] = Query(None, description="Filter wishlist items"),
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Get all books for the current user with optional filters"""
    query = db.query(models.Book).filter(models.Book.user_id == current_user.id)

    if reading_status:
        query = query.filter(models.Book.reading_status == reading_status)

    if is_wishlist is not None:
        query = query.filter(models.Book.is_wishlist == is_wishlist)

    books = query.order_by(models.Book.added_at.desc()).all()
    return books


@router.get("/{book_id}", response_model=schemas.Book)
def get_book(
    book_id: int,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Get a specific book by ID"""
    book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    return book


@router.patch("/{book_id}", response_model=schemas.Book)
def update_book(
    book_id: int,
    book_update: schemas.BookUpdate,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Update book details (reading status, notes, etc.)"""
    db_book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()
    
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update only provided fields
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)
    
    db.commit()
    db.refresh(db_book)
    
    return db_book


@router.post("/{book_id}/refresh-metadata", response_model=schemas.Book)
async def refresh_book_metadata(
    book_id: int,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Refresh book metadata from Google Books and Open Library APIs"""
    db_book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()

    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Try to fetch updated info from Google Books using ISBN or title
    book_info = None
    if db_book.isbn:
        book_info = await google_books_service.search_by_isbn(db_book.isbn)

    if not book_info and db_book.title:
        # Try searching by title and author
        search_query = db_book.title
        if db_book.authors:
            search_query += f" {db_book.authors.split(',')[0]}"
        results = await google_books_service.search_by_title(search_query, max_results=1)
        if results:
            book_info = results[0]

    if book_info:
        # Update fields that might have changed, but preserve user data
        if book_info.series_name:
            db_book.series_name = book_info.series_name
        if book_info.series_position:
            db_book.series_position = book_info.series_position
        if book_info.thumbnail and not db_book.thumbnail:
            db_book.thumbnail = book_info.thumbnail
        if book_info.description and not db_book.description:
            db_book.description = book_info.description

        db.commit()
        db.refresh(db_book)

    return db_book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Delete a book from library"""
    db_book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()

    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    db.delete(db_book)
    db.commit()

    return None

