import httpx
import re
from typing import Optional, Tuple, List

class OpenLibraryService:
    """Service for fetching book series information and cover art from Open Library API"""
    BASE_URL = "https://openlibrary.org"
    COVERS_URL = "https://covers.openlibrary.org/b"
    
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

            # Check if the cover exists by making a HEAD request
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.head(cover_url)

                if response.status_code == 200:
                    return cover_url

                return None

        except Exception as e:
            print(f"Error fetching cover from Open Library: {e}")
            return None


openlibrary_service = OpenLibraryService()

