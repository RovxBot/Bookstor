from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth
from ..database import get_db
from ..services.google_books import google_books_service
from ..services.openlibrary import openlibrary_service
from ..services.api_integration_manager import api_integration_manager

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/search", response_model=List[schemas.GoogleBookInfo])
@router.get("/search/", response_model=List[schemas.GoogleBookInfo])
async def search_books(
    q: str = Query(..., description="Search query (title, author, etc.)"),
    max_results: int = Query(10, ge=1, le=40, description="Maximum number of results"),
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Search for books using all enabled API integrations"""
    results = await api_integration_manager.search_by_title(q, db, max_results)
    return results


@router.post("/isbn/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
async def add_book_by_isbn(
    isbn_lookup: schemas.ISBNLookup,
    current_user: models.User = Depends(auth.get_current_user_flexible),
    db: Session = Depends(get_db)
):
    """Add a book to library by scanning ISBN - uses all enabled API integrations"""
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

    # Use API integration manager to search across all enabled APIs
    book_info = await api_integration_manager.search_by_isbn(isbn_lookup.isbn, db)

    if not book_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in any configured API"
        )

    # Extract data from merged book info
    title = book_info.title or "Unknown Title"
    subtitle = book_info.subtitle

    # Authors
    authors = None
    if book_info.authors:
        authors = ", ".join(book_info.authors)

    # Other fields
    description = book_info.description
    publisher = book_info.publisher
    published_date = book_info.published_date
    page_count = book_info.page_count

    # Categories
    categories = None
    if book_info.categories:
        categories = ", ".join(book_info.categories)

    # Thumbnail, series, edition, format
    thumbnail = book_info.thumbnail
    series_name = book_info.series_name
    series_position = book_info.series_position
    edition = book_info.edition
    book_format = book_info.book_format
    google_books_id = book_info.google_books_id

    # Create book entry
    db_book = models.Book(
        user_id=current_user.id,
        isbn=isbn_lookup.isbn,
        google_books_id=google_books_id,
        title=title,
        subtitle=subtitle,
        authors=authors,
        description=description,
        publisher=publisher,
        published_date=published_date,
        page_count=page_count,
        categories=categories,
        thumbnail=thumbnail,
        series_name=series_name,
        series_position=series_position,
        edition=edition,
        book_format=book_format,
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
    """Refresh book metadata from all enabled API integrations"""
    db_book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()

    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Try to fetch updated metadata using API integration manager
    book_info = None
    if db_book.isbn:
        book_info = await api_integration_manager.search_by_isbn(db_book.isbn, db)
    elif db_book.title:
        # Try searching by title and author if no ISBN
        search_query = db_book.title
        if db_book.authors:
            search_query += f" {db_book.authors.split(',')[0]}"
        results = await api_integration_manager.search_by_title(search_query, db, max_results=1)
        if results:
            book_info = results[0]

    # Update all metadata fields with merged data
    if book_info:
        # Update fields if new data is available
        if book_info.title:
            db_book.title = book_info.title
        if book_info.subtitle:
            db_book.subtitle = book_info.subtitle

        # Authors
        if book_info.authors:
            db_book.authors = ", ".join(book_info.authors)

        # Description
        if book_info.description:
            db_book.description = book_info.description

        # Publisher and published date
        if book_info.publisher:
            db_book.publisher = book_info.publisher
        if book_info.published_date:
            db_book.published_date = book_info.published_date

        # Page count
        if book_info.page_count:
            db_book.page_count = book_info.page_count

        # Categories
        if book_info.categories:
            db_book.categories = ", ".join(book_info.categories)

        # Thumbnail
        if book_info.thumbnail:
            db_book.thumbnail = book_info.thumbnail

        # Series information
        if book_info.series_name:
            db_book.series_name = book_info.series_name
        if book_info.series_position:
            db_book.series_position = book_info.series_position

        # Edition and format
        if book_info.edition:
            db_book.edition = book_info.edition
        if book_info.book_format:
            db_book.book_format = book_info.book_format

        # Google Books ID
        if book_info.google_books_id:
            db_book.google_books_id = book_info.google_books_id

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

