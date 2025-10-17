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
    """Add a book to library by scanning ISBN - tries Open Library first, then Google Books"""
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

    # Try Open Library first (primary source)
    ol_book_info = await openlibrary_service.search_by_isbn(isbn_lookup.isbn)

    # Try Google Books as fallback
    gb_book_info = await google_books_service.search_by_isbn(isbn_lookup.isbn)

    if not ol_book_info and not gb_book_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found in Open Library or Google Books database"
        )

    # Merge data: prefer Open Library, fill gaps with Google Books
    title = (ol_book_info.title if ol_book_info else None) or (gb_book_info.title if gb_book_info else "Unknown Title")
    subtitle = (ol_book_info.subtitle if ol_book_info else None) or (gb_book_info.subtitle if gb_book_info else None)

    # Authors
    authors = None
    if ol_book_info and ol_book_info.authors:
        authors = ", ".join(ol_book_info.authors)
    elif gb_book_info and gb_book_info.authors:
        authors = ", ".join(gb_book_info.authors)

    # Description
    description = (ol_book_info.description if ol_book_info else None) or (gb_book_info.description if gb_book_info else None)

    # Publisher and published date
    publisher = (ol_book_info.publisher if ol_book_info else None) or (gb_book_info.publisher if gb_book_info else None)
    published_date = (ol_book_info.published_date if ol_book_info else None) or (gb_book_info.published_date if gb_book_info else None)

    # Page count
    page_count = (ol_book_info.page_count if ol_book_info else None) or (gb_book_info.page_count if gb_book_info else None)

    # Categories
    categories = None
    if ol_book_info and ol_book_info.categories:
        categories = ", ".join(ol_book_info.categories)
    elif gb_book_info and gb_book_info.categories:
        categories = ", ".join(gb_book_info.categories)

    # Thumbnail
    thumbnail = (ol_book_info.thumbnail if ol_book_info else None) or (gb_book_info.thumbnail if gb_book_info else None)

    # Series information
    series_name = (ol_book_info.series_name if ol_book_info else None) or (gb_book_info.series_name if gb_book_info else None)
    series_position = (ol_book_info.series_position if ol_book_info else None) or (gb_book_info.series_position if gb_book_info else None)

    # Edition and format (Open Library specific)
    edition = ol_book_info.edition if ol_book_info else None
    book_format = ol_book_info.book_format if ol_book_info else None

    # Google Books ID
    google_books_id = gb_book_info.google_books_id if gb_book_info else None

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
    """Refresh book metadata from Open Library and Google Books APIs (Open Library primary)"""
    db_book = db.query(models.Book).filter(
        models.Book.id == book_id,
        models.Book.user_id == current_user.id
    ).first()

    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Try Open Library first if we have ISBN
    ol_book_info = None
    if db_book.isbn:
        ol_book_info = await openlibrary_service.search_by_isbn(db_book.isbn)

    # Try Google Books as fallback
    gb_book_info = None
    if db_book.isbn:
        gb_book_info = await google_books_service.search_by_isbn(db_book.isbn)
    elif db_book.title:
        # Try searching by title and author if no ISBN
        search_query = db_book.title
        if db_book.authors:
            search_query += f" {db_book.authors.split(',')[0]}"
        results = await google_books_service.search_by_title(search_query, max_results=1)
        if results:
            gb_book_info = results[0]

    # Update all metadata fields, preferring Open Library data
    if ol_book_info or gb_book_info:
        # Title and subtitle
        if ol_book_info and ol_book_info.title:
            db_book.title = ol_book_info.title
        elif gb_book_info and gb_book_info.title:
            db_book.title = gb_book_info.title

        if ol_book_info and ol_book_info.subtitle:
            db_book.subtitle = ol_book_info.subtitle
        elif gb_book_info and gb_book_info.subtitle:
            db_book.subtitle = gb_book_info.subtitle

        # Authors
        if ol_book_info and ol_book_info.authors:
            db_book.authors = ", ".join(ol_book_info.authors)
        elif gb_book_info and gb_book_info.authors:
            db_book.authors = ", ".join(gb_book_info.authors)

        # Description
        if ol_book_info and ol_book_info.description:
            db_book.description = ol_book_info.description
        elif gb_book_info and gb_book_info.description:
            db_book.description = gb_book_info.description

        # Publisher and published date
        if ol_book_info and ol_book_info.publisher:
            db_book.publisher = ol_book_info.publisher
        elif gb_book_info and gb_book_info.publisher:
            db_book.publisher = gb_book_info.publisher

        if ol_book_info and ol_book_info.published_date:
            db_book.published_date = ol_book_info.published_date
        elif gb_book_info and gb_book_info.published_date:
            db_book.published_date = gb_book_info.published_date

        # Page count
        if ol_book_info and ol_book_info.page_count:
            db_book.page_count = ol_book_info.page_count
        elif gb_book_info and gb_book_info.page_count:
            db_book.page_count = gb_book_info.page_count

        # Categories
        if ol_book_info and ol_book_info.categories:
            db_book.categories = ", ".join(ol_book_info.categories)
        elif gb_book_info and gb_book_info.categories:
            db_book.categories = ", ".join(gb_book_info.categories)

        # Thumbnail
        if ol_book_info and ol_book_info.thumbnail:
            db_book.thumbnail = ol_book_info.thumbnail
        elif gb_book_info and gb_book_info.thumbnail:
            db_book.thumbnail = gb_book_info.thumbnail

        # Series information
        if ol_book_info and ol_book_info.series_name:
            db_book.series_name = ol_book_info.series_name
        elif gb_book_info and gb_book_info.series_name:
            db_book.series_name = gb_book_info.series_name

        if ol_book_info and ol_book_info.series_position:
            db_book.series_position = ol_book_info.series_position
        elif gb_book_info and gb_book_info.series_position:
            db_book.series_position = gb_book_info.series_position

        # Edition and format (Open Library specific)
        if ol_book_info and ol_book_info.edition:
            db_book.edition = ol_book_info.edition
        if ol_book_info and ol_book_info.book_format:
            db_book.book_format = ol_book_info.book_format

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

