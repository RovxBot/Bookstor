import httpx
import re
from typing import Optional, Tuple, List, Dict, Any
from pydantic import BaseModel

class OpenLibraryBookInfo(BaseModel):
    """Book information from Open Library API"""
    title: str
    subtitle: Optional[str] = None
    authors: Optional[List[str]] = None
    description: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    categories: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    isbn: Optional[str] = None
    series_name: Optional[str] = None
    series_position: Optional[str] = None
    edition: Optional[str] = None
    book_format: Optional[str] = None  # paperback, hardcover, etc.

class OpenLibraryService:
    """Service for fetching book information from Open Library API"""
    BASE_URL = "https://openlibrary.org"
    COVERS_URL = "https://covers.openlibrary.org/b"

    async def search_by_isbn(self, isbn: str) -> Optional[OpenLibraryBookInfo]:
        """
        Search for a book by ISBN using Open Library API
        Returns: OpenLibraryBookInfo object if found, None otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search for the book by ISBN
                params = {
                    'q': f'isbn:{isbn}',
                    'limit': 1
                }
                response = await client.get(f"{self.BASE_URL}/search.json", params=params)

                if response.status_code != 200:
                    return None

                data = response.json()
                docs = data.get('docs', [])

                if not docs:
                    return None

                doc = docs[0]

                # Get the edition key to fetch more detailed information
                edition_key = doc.get('edition_key', [None])[0] if doc.get('edition_key') else None

                # Fetch edition details if available
                edition_data = None
                if edition_key:
                    edition_response = await client.get(f"{self.BASE_URL}/books/{edition_key}.json")
                    if edition_response.status_code == 200:
                        edition_data = edition_response.json()

                # Get work key for series and description
                work_key = doc.get('key')
                work_data = None
                if work_key:
                    work_response = await client.get(f"{self.BASE_URL}{work_key}.json")
                    if work_response.status_code == 200:
                        work_data = work_response.json()

                # Extract all book information
                title = doc.get('title', 'Unknown Title')
                subtitle = doc.get('subtitle') or (edition_data.get('subtitle') if edition_data else None)
                authors = doc.get('author_name', [])

                # Get description from work data or edition data
                description = None
                if work_data:
                    desc = work_data.get('description')
                    if isinstance(desc, dict):
                        description = desc.get('value')
                    elif isinstance(desc, str):
                        description = desc
                if not description and edition_data:
                    desc = edition_data.get('description')
                    if isinstance(desc, dict):
                        description = desc.get('value')
                    elif isinstance(desc, str):
                        description = desc

                # Publisher and published date
                publisher = doc.get('publisher', [None])[0] if doc.get('publisher') else None
                published_date = doc.get('publish_date', [None])[0] if doc.get('publish_date') else None
                if not published_date:
                    published_date = str(doc.get('first_publish_year')) if doc.get('first_publish_year') else None

                # Page count
                page_count = doc.get('number_of_pages_median')
                if not page_count and edition_data:
                    page_count = edition_data.get('number_of_pages')

                # Categories (subjects)
                categories = doc.get('subject', [])[:5]  # Limit to first 5 subjects

                # Cover image - try multiple methods
                thumbnail = None
                # Method 1: Try cover_i from search results
                cover_i = doc.get('cover_i')
                if cover_i:
                    thumbnail = f"{self.COVERS_URL}/id/{cover_i}-L.jpg"
                # Method 2: Try ISBN-based cover
                if not thumbnail:
                    thumbnail = await self.get_cover_by_isbn(isbn, size="L")
                # Method 3: Try edition cover
                if not thumbnail and edition_data:
                    covers = edition_data.get('covers', [])
                    if covers:
                        thumbnail = f"{self.COVERS_URL}/id/{covers[0]}-L.jpg"

                # Series information
                series_name, series_position = None, None
                if work_data:
                    series_name, series_position = self._extract_series_from_work(work_data)
                if not series_name:
                    # Try extracting from title
                    series_name, series_position = self._extract_series_from_title(title, subtitle)

                # Edition information
                edition = None
                if edition_data:
                    edition = edition_data.get('edition_name')

                # Format (paperback/hardcover)
                book_format_type = None
                if edition_data:
                    physical_format = edition_data.get('physical_format', '').lower()
                    if 'paperback' in physical_format or 'mass market' in physical_format:
                        book_format_type = 'Paperback'
                    elif 'hardcover' in physical_format or 'hardback' in physical_format:
                        book_format_type = 'Hardcover'
                    elif physical_format:
                        book_format_type = physical_format.title()

                return OpenLibraryBookInfo(
                    title=title,
                    subtitle=subtitle,
                    authors=authors if authors else None,
                    description=description,
                    publisher=publisher,
                    published_date=published_date,
                    page_count=page_count,
                    categories=categories if categories else None,
                    thumbnail=thumbnail,
                    isbn=isbn,
                    series_name=series_name,
                    series_position=series_position,
                    edition=edition,
                    book_format=book_format_type
                )

        except Exception as e:
            print(f"Error fetching book data from Open Library: {e}")
            return None

    def _extract_series_from_title(self, title: str, subtitle: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract series information from title and subtitle
        Returns: (series_name, series_position)
        """
        full_title = f"{title} {subtitle}" if subtitle else title

        # Patterns to extract series and position
        patterns = [
            r'(.+?)\s+(?:Book|#|Vol\.?|Volume)\s+(\d+)',
            r'(.+?)\s+\((\d+)\)',
            r'(.+?):\s+Book\s+(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, full_title, re.IGNORECASE)
            if match:
                series_name = match.group(1).strip()
                series_position = match.group(2)
                # Clean up series name
                series_name = re.sub(r'\s+(?:Series|Saga|Trilogy|Chronicles)$', '', series_name, flags=re.IGNORECASE).strip()
                return series_name, series_position

        return None, None

    async def get_series_info_by_isbn(self, isbn: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Get series information for a book by ISBN from Open Library
        Returns: (series_name, series_position)
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search for the book by ISBN
                params = {
                    'q': f'isbn:{isbn}',
                    'limit': 1
                }
                response = await client.get(f"{self.BASE_URL}/search.json", params=params)

                if response.status_code != 200:
                    return None, None

                data = response.json()
                docs = data.get('docs', [])

                if not docs:
                    return None, None

                # Get the work key from the first result
                work_key = docs[0].get('key')  # e.g., "/works/OL257943W"

                if not work_key:
                    return None, None

                # Fetch the work details
                work_response = await client.get(f"{self.BASE_URL}{work_key}.json")

                if work_response.status_code != 200:
                    return None, None

                work_data = work_response.json()

                # Extract series information from subjects
                series_name, series_position = self._extract_series_from_work(work_data)

                return series_name, series_position

        except Exception as e:
            print(f"Error fetching series info from Open Library: {e}")
            return None, None
    
    def _extract_series_from_work(self, work_data: dict) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract series information from Open Library work data
        Returns: (series_name, series_position)
        """
        series_name = None
        series_position = None
        
        # Check subjects for series information
        subjects = work_data.get('subjects', [])
        
        for subject in subjects:
            # Look for "series:Series Name" pattern
            if isinstance(subject, str) and subject.lower().startswith('series:'):
                series_name = subject[7:].strip()  # Remove "series:" prefix
                break
        
        # Try to extract position from title if we found a series
        if series_name:
            title = work_data.get('title', '')
            series_position = self._extract_position_from_title(title)
        
        return series_name, series_position
    
    def _extract_position_from_title(self, title: str) -> Optional[str]:
        """
        Extract book position/number from title
        Returns: position as string (e.g., "1", "2", "3")
        """
        # Patterns to extract position
        patterns = [
            r'Book\s+(\d+)',
            r'#(\d+)',
            r'Vol\.?\s+(\d+)',
            r'Volume\s+(\d+)',
            r'\((\d+)\)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    async def search_series_books(self, series_name: str, limit: int = 20) -> List[dict]:
        """
        Search for all books in a series
        Returns: List of books with title, author, and position
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Search for books with the series name
                params = {
                    'q': f'series:"{series_name}"',
                    'limit': limit,
                    'fields': 'key,title,author_name,first_publish_year,cover_i'
                }
                
                response = await client.get(
                    f"{self.BASE_URL}/search.json",
                    params=params
                )
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                docs = data.get('docs', [])
                
                books = []
                for doc in docs:
                    title = doc.get('title', '')
                    position = self._extract_position_from_title(title)
                    
                    book_info = {
                        'title': title,
                        'author': doc.get('author_name', ['Unknown'])[0] if doc.get('author_name') else 'Unknown',
                        'position': position,
                        'first_publish_year': doc.get('first_publish_year'),
                        'work_key': doc.get('key'),
                    }
                    books.append(book_info)
                
                # Sort by position if available
                books_with_position = [b for b in books if b['position']]
                books_without_position = [b for b in books if not b['position']]
                
                books_with_position.sort(key=lambda x: int(x['position']))
                
                return books_with_position + books_without_position
                
        except Exception as e:
            print(f"Error searching series books from Open Library: {e}")
            return []


    async def get_cover_by_isbn(self, isbn: str, size: str = "L") -> Optional[str]:
        """
        Get cover image URL from Open Library by ISBN
        Args:
            isbn: The ISBN-10 or ISBN-13
            size: S (small), M (medium), or L (large)
        Returns:
            Cover image URL or None
        """
        try:
            # Open Library covers API: https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg
            cover_url = f"{self.COVERS_URL}/isbn/{isbn}-{size}.jpg"

            # Check if the cover exists by making a HEAD request with follow_redirects
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                response = await client.head(cover_url)

                # Check if we got a valid image response
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    # Make sure it's actually an image, not a placeholder
                    if 'image' in content_type:
                        # Return the final URL after redirects
                        return str(response.url)

                return None

        except Exception as e:
            print(f"Error fetching cover from Open Library: {e}")
            return None


openlibrary_service = OpenLibraryService()

