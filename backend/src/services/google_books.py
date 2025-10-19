import httpx
import re
from typing import Optional, Tuple
from ..schemas import GoogleBookInfo
from ..config import settings
from .openlibrary import openlibrary_service


class GoogleBooksService:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def _extract_series_info(self, title: str, subtitle: Optional[str], categories: Optional[list]) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract series name and position from title, subtitle, or categories
        Returns: (series_name, series_position)
        """
        series_name = None
        series_position = None

        # Combine title and subtitle for analysis
        full_title = f"{title} {subtitle}" if subtitle else title

        # Known series mappings (for books where Google doesn't provide series info)
        known_series = {
            'A Game of Thrones': ('A Song of Ice and Fire', '1'),
            'A Clash of Kings': ('A Song of Ice and Fire', '2'),
            'A Storm of Swords': ('A Song of Ice and Fire', '3'),
            'A Feast for Crows': ('A Song of Ice and Fire', '4'),
            'A Dance with Dragons': ('A Song of Ice and Fire', '5'),
            'The Winds of Winter': ('A Song of Ice and Fire', '6'),
            'A Dream of Spring': ('A Song of Ice and Fire', '7'),
            # Rain Wild Chronicles by Robin Hobb
            'Dragon Keeper': ('Rain Wild Chronicles', '1'),
            'Dragon Haven': ('Rain Wild Chronicles', '2'),
            'City of Dragons': ('Rain Wild Chronicles', '3'),
            'Blood of Dragons': ('Rain Wild Chronicles', '4'),
            # Tawny Man Trilogy by Robin Hobb
            "Fool's Errand": ('Tawny Man', '1'),
            "Golden Fool": ('Tawny Man', '2'),
            "Fool's Fate": ('Tawny Man', '3'),
        }

        # Check if this is a known series book
        if title in known_series:
            series_name, series_position = known_series[title]
            return series_name, series_position

        # Patterns to extract series info
        patterns = [
            # "Book Title (Series Name, #1)" or "Book Title (Series Name #1)"
            (r'\(([^)]+?)[,\s]+#?(\d+)\)', 1, 2),
            # "Book Title (Series Name Book 1)"
            (r'\(([^)]+?)\s+Book\s+(\d+)\)', 1, 2),
            # "Series Name: Book Title" - series before colon
            (r'^([^:]+?):\s+', 1, None),
            # "Series Name - Book Title" - series before dash
            (r'^([^-]+?)\s+-\s+', 1, None),
            # "Series Name Book 1" or "Series Name Vol 1"
            (r'^(.+?)\s+(?:Book|Vol\.?|Volume)\s+(\d+)', 1, 2),
            # "Series Name #1"
            (r'^(.+?)\s+#(\d+)', 1, 2),
            # "Part 1", "Part 2" etc
            (r'Part\s+(\d+)', None, 1),
        ]

        for pattern, name_group, pos_group in patterns:
            match = re.search(pattern, full_title, re.IGNORECASE)
            if match:
                if name_group:
                    series_name = match.group(name_group).strip()
                if pos_group and len(match.groups()) >= pos_group:
                    series_position = match.group(pos_group)
                if series_name:  # Only break if we found a series name
                    break

        # Check categories for series info if not found in title
        if not series_name and categories:
            for category in categories:
                # Look for patterns like "Fiction / Series Name" or just "Series Name"
                if '/' in category:
                    parts = category.split('/')
                    for part in parts:
                        part = part.strip()
                        if any(keyword in part.lower() for keyword in ['series', 'saga', 'trilogy', 'chronicles']):
                            series_name = part
                            break

        # Clean up series name
        if series_name:
            # Remove common suffixes
            series_name = re.sub(r'\s+(?:Series|Saga|Trilogy|Chronicles)$', '', series_name, flags=re.IGNORECASE).strip()
            # Remove leading "The" for consistency
            series_name = re.sub(r'^The\s+', '', series_name, flags=re.IGNORECASE).strip()

        return series_name, series_position

    async def search_by_isbn(self, isbn: str) -> Optional[GoogleBookInfo]:
        """
        Search for a book by ISBN using Google Books API
        
        Args:
            isbn: The ISBN-10 or ISBN-13 of the book
            
        Returns:
            GoogleBookInfo object if found, None otherwise
        """
        params = {
            "q": f"isbn:{isbn}",
        }
        
        if settings.google_books_api_key:
            params["key"] = settings.google_books_api_key
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data.get("totalItems", 0) == 0:
                    return None
                
                # Get the first result
                item = data["items"][0]
                volume_info = item.get("volumeInfo", {})

                # Extract ISBN from industryIdentifiers
                extracted_isbn = None
                industry_identifiers = volume_info.get("industryIdentifiers", [])
                for identifier in industry_identifiers:
                    id_type = identifier.get("type", "")
                    id_value = identifier.get("identifier", "")
                    # Prefer ISBN_13, but accept ISBN_10 if that's all we have
                    if id_type == "ISBN_13":
                        extracted_isbn = id_value
                        break
                    elif id_type == "ISBN_10" and not extracted_isbn:
                        extracted_isbn = id_value

                # If we didn't find an ISBN in the response, use the search ISBN
                if not extracted_isbn:
                    extracted_isbn = isbn
                    print(f"Warning: Google Books didn't return ISBN in industryIdentifiers, using search ISBN: {isbn}")

                # Extract thumbnail (prefer larger image)
                thumbnail = None
                if "imageLinks" in volume_info:
                    thumbnail = (
                        volume_info["imageLinks"].get("thumbnail") or
                        volume_info["imageLinks"].get("smallThumbnail")
                    )

                # If no thumbnail from Google Books, try Open Library
                if not thumbnail:
                    thumbnail = await openlibrary_service.get_cover_by_isbn(isbn, size="L")

                # Extract series information
                title = volume_info.get("title", "Unknown Title")
                subtitle = volume_info.get("subtitle")
                categories = volume_info.get("categories")

                # Try to get series info from our local extraction first
                series_name, series_position = self._extract_series_info(title, subtitle, categories)

                # If no series found, try Open Library as fallback
                if not series_name:
                    ol_series, ol_position = await openlibrary_service.get_series_info_by_isbn(isbn)
                    if ol_series:
                        series_name = ol_series
                        series_position = ol_position or series_position

                return GoogleBookInfo(
                    title=title,
                    subtitle=subtitle,
                    authors=volume_info.get("authors"),
                    description=volume_info.get("description"),
                    publisher=volume_info.get("publisher"),
                    published_date=volume_info.get("publishedDate"),
                    page_count=volume_info.get("pageCount"),
                    categories=categories,
                    thumbnail=thumbnail,
                    isbn=extracted_isbn,  # Add the extracted ISBN
                    google_books_id=item.get("id"),
                    series_name=series_name,
                    series_position=series_position
                )
                
            except httpx.HTTPError as e:
                print(f"Error fetching book data from Google Books: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

    async def search_by_title(self, query: str, max_results: int = 10) -> list[GoogleBookInfo]:
        """
        Search for books by title using Google Books API

        Args:
            query: The search query (title, author, etc.)
            max_results: Maximum number of results to return (default: 10)

        Returns:
            List of GoogleBookInfo objects
        """
        params = {
            "q": query,
            "maxResults": min(max_results, 40),  # API limit is 40
        }

        if settings.google_books_api_key:
            params["key"] = settings.google_books_api_key

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()

                if data.get("totalItems", 0) == 0:
                    return []

                results = []
                for item in data.get("items", []):
                    volume_info = item.get("volumeInfo", {})

                    # Extract ISBN if available
                    isbn = None
                    for identifier in volume_info.get("industryIdentifiers", []):
                        if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                            isbn = identifier.get("identifier")
                            break

                    # Extract thumbnail (prefer larger image)
                    thumbnail = None
                    if "imageLinks" in volume_info:
                        thumbnail = (
                            volume_info["imageLinks"].get("thumbnail") or
                            volume_info["imageLinks"].get("smallThumbnail")
                        )

                    # If no thumbnail from Google Books and we have ISBN, try Open Library
                    if not thumbnail and isbn:
                        thumbnail = await openlibrary_service.get_cover_by_isbn(isbn, size="L")

                    # Extract series information
                    title = volume_info.get("title", "Unknown Title")
                    subtitle = volume_info.get("subtitle")
                    categories = volume_info.get("categories")
                    series_name, series_position = self._extract_series_info(title, subtitle, categories)

                    # If no series found and we have ISBN, try Open Library as fallback
                    if not series_name and isbn:
                        ol_series, ol_position = await openlibrary_service.get_series_info_by_isbn(isbn)
                        if ol_series:
                            series_name = ol_series
                            series_position = ol_position or series_position

                    book_info = GoogleBookInfo(
                        title=title,
                        subtitle=subtitle,
                        authors=volume_info.get("authors"),
                        description=volume_info.get("description"),
                        publisher=volume_info.get("publisher"),
                        published_date=volume_info.get("publishedDate"),
                        page_count=volume_info.get("pageCount"),
                        categories=categories,
                        thumbnail=thumbnail,
                        google_books_id=item.get("id"),
                        isbn=isbn,
                        series_name=series_name,
                        series_position=series_position
                    )
                    results.append(book_info)

                return results

            except httpx.HTTPError as e:
                print(f"Error fetching book data from Google Books: {e}")
                return []
            except Exception as e:
                print(f"Unexpected error: {e}")
                return []


google_books_service = GoogleBooksService()

