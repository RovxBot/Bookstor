"""
Hardcover API Service
Handles book metadata fetching from Hardcover's GraphQL API
"""
import httpx
from typing import Optional, List
from ..schemas import GoogleBookInfo


class HardcoverService:
    """Service for fetching book information from Hardcover GraphQL API"""
    
    BASE_URL = "https://api.hardcover.app/v1/graphql"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise Hardcover service
        Args:
            api_key: Hardcover API token (required)
        """
        self.api_key = api_key
    
    async def search_by_isbn(self, isbn: str) -> Optional[GoogleBookInfo]:
        """
        Search for a book by ISBN using Hardcover's GraphQL API
        Args:
            isbn: The ISBN-10 or ISBN-13 to search for
        Returns:
            GoogleBookInfo object or None if not found
        """
        if not self.api_key:
            print("Hardcover API key not configured")
            return None
        
        # GraphQL query to search for book by ISBN
        # Use the search API instead of direct book query
        query = """
        query SearchByISBN($isbn: String!) {
          search(
            query: $isbn,
            query_type: "books",
            per_page: 1,
            page: 1
          ) {
            results
          }
        }
        """
        
        variables = {"isbn": isbn}
        
        try:
            # Prepare authorization header
            auth_header = self.api_key
            if not auth_header.startswith("Bearer "):
                auth_header = f"Bearer {auth_header}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    json={"query": query, "variables": variables},
                    headers={
                        "Authorization": auth_header,
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    print(f"Hardcover API error: {response.status_code}")
                    return None
                
                data = response.json()
                
                # Check for GraphQL errors
                if "errors" in data:
                    print(f"Hardcover GraphQL errors: {data['errors']}")
                    return None

                # Extract search results - Hardcover returns a dict with 'hits' key
                search_data = data.get("data", {}).get("search", {}).get("results", {})
                hits = search_data.get("hits", [])

                if not hits or len(hits) == 0:
                    return None

                # Parse the first hit - the actual book data is in 'document'
                first_hit = hits[0]
                book = first_hit.get("document", {})

                return self._parse_search_result_for_isbn(book, isbn)
                
        except Exception as e:
            print(f"Error fetching from Hardcover: {e}")
            return None
    
    async def search_by_title(self, query: str, max_results: int = 10) -> List[GoogleBookInfo]:
        """
        Search for books by title using Hardcover's search API
        Args:
            query: The search query
            max_results: Maximum number of results to return
        Returns:
            List of GoogleBookInfo objects
        """
        if not self.api_key:
            print("Hardcover API key not configured")
            return []
        
        # GraphQL query using Hardcover's search
        graphql_query = """
        query Search($title: String!, $perPage: Int!) {
          search(
            query: $title,
            query_type: "books",
            per_page: $perPage,
            page: 1,
            sort: "activities_count:desc"
          ) {
            results
          }
        }
        """
        
        variables = {
            "title": query,
            "perPage": max_results
        }
        
        try:
            # Prepare authorization header
            auth_header = self.api_key
            if not auth_header.startswith("Bearer "):
                auth_header = f"Bearer {auth_header}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.BASE_URL,
                    json={"query": graphql_query, "variables": variables},
                    headers={
                        "Authorization": auth_header,
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    print(f"Hardcover API error: {response.status_code}")
                    return []
                
                data = response.json()
                
                # Check for GraphQL errors
                if "errors" in data:
                    print(f"Hardcover GraphQL errors: {data['errors']}")
                    return []

                # Extract search results - Hardcover returns a dict with 'hits' key
                search_data = data.get("data", {}).get("search", {}).get("results", {})
                hits = search_data.get("hits", [])

                books = []
                for hit in hits[:max_results]:
                    book = hit.get("document", {})
                    parsed = self._parse_search_result(book)
                    if parsed:
                        books.append(parsed)

                return books
                
        except Exception as e:
            print(f"Error searching Hardcover: {e}")
            return []
    
    def _parse_book_data(self, book: dict, isbn: str) -> Optional[GoogleBookInfo]:
        """
        Parse Hardcover book data into GoogleBookInfo format
        Args:
            book: Raw book data from Hardcover API
            isbn: The ISBN that was searched for
        Returns:
            GoogleBookInfo object or None
        """
        try:
            # Extract authors from cached_contributors
            authors = []
            cached_contributors = book.get("cached_contributors", [])
            if cached_contributors:
                for contributor in cached_contributors:
                    if isinstance(contributor, dict):
                        author_data = contributor.get("author", {})
                        if isinstance(author_data, dict):
                            name = author_data.get("name")
                            if name:
                                authors.append(name)
            
            # Extract genre from cached_tags
            categories = []
            cached_tags = book.get("cached_tags", {})
            if isinstance(cached_tags, dict):
                genre_tags = cached_tags.get("Genre", [])
                if genre_tags:
                    # Take the first genre tag (most popular)
                    categories = [genre_tags[0]] if genre_tags else []
            
            # Extract series information
            series_name = None
            series_position = None
            series_data = book.get("series")
            if series_data and isinstance(series_data, dict):
                series_name = series_data.get("name")
            
            book_series = book.get("book_series", [])
            if book_series and isinstance(book_series, list) and len(book_series) > 0:
                series_position = str(book_series[0].get("position", ""))
            
            # Extract edition and format from editions
            edition = None
            book_format = None
            editions = book.get("editions", [])
            if editions and isinstance(editions, list):
                for ed in editions:
                    if isinstance(ed, dict):
                        if not edition and ed.get("title"):
                            edition = ed.get("title")
                        if not book_format and ed.get("format"):
                            book_format = ed.get("format")
                        if edition and book_format:
                            break
            
            # Build published date from release_year
            published_date = None
            release_year = book.get("release_year")
            if release_year:
                published_date = str(release_year)
            
            return GoogleBookInfo(
                title=book.get("title"),
                subtitle=book.get("subtitle"),
                authors=authors if authors else None,
                description=book.get("description"),
                publisher=None,  # Hardcover doesn't provide publisher in basic query
                published_date=published_date,
                page_count=book.get("pages"),
                categories=categories if categories else None,
                thumbnail=book.get("image"),
                isbn=isbn,
                series_name=series_name,
                series_position=series_position,
                edition=edition,
                book_format=book_format,
                google_books_id=None
            )
        except Exception as e:
            print(f"Error parsing Hardcover book data: {e}")
            return None
    
    def _parse_search_result(self, result: dict) -> Optional[GoogleBookInfo]:
        """
        Parse Hardcover search result into GoogleBookInfo format
        The search API returns a blob of data that needs parsing
        """
        try:
            # Search results come as a dict with various fields
            # Extract what we can
            isbn = result.get("isbn_13") or result.get("isbn_10")

            if isbn:
                return self._parse_book_data(result, isbn)

            return None
        except Exception as e:
            print(f"Error parsing Hardcover search result: {e}")
            return None

    def _parse_search_result_for_isbn(self, result: dict, isbn: str) -> Optional[GoogleBookInfo]:
        """
        Parse Hardcover search result for ISBN search
        The search API returns a blob of data that needs parsing
        """
        try:
            # Extract basic fields from search result
            title = result.get("title")
            if not title:
                return None

            # Extract authors from author_names (simpler field)
            authors = result.get("author_names", [])

            # Extract other fields
            description = result.get("description")
            pages = result.get("pages")
            release_year = result.get("release_year")

            # Extract image - it's a dict with 'url' key
            image_data = result.get("image")
            image_url = None
            if isinstance(image_data, dict):
                image_url = image_data.get("url")
            elif isinstance(image_data, str):
                image_url = image_data

            # Extract genres from genres list
            genres = result.get("genres", [])
            categories = genres[:3] if genres else None  # Take first 3 genres

            # Extract series information
            series_name = None
            series_position = None
            featured_series = result.get("featured_series")
            if featured_series and isinstance(featured_series, dict):
                series_data = featured_series.get("series", {})
                if isinstance(series_data, dict):
                    series_name = series_data.get("name")
                series_position = featured_series.get("position")
                if series_position is not None:
                    series_position = str(series_position)

            # Build published date
            published_date = str(release_year) if release_year else None

            return GoogleBookInfo(
                title=title,
                subtitle=result.get("subtitle"),
                authors=authors if authors else None,
                description=description,
                publisher=None,  # Not in search results
                published_date=published_date,
                page_count=pages,
                categories=categories,
                thumbnail=image_url,
                isbn=isbn,
                series_name=series_name,
                series_position=series_position,
                edition=None,  # Not in search results
                book_format=None,  # Not in search results
                google_books_id=None
            )
        except Exception as e:
            print(f"Error parsing Hardcover search result for ISBN: {e}")
            import traceback
            traceback.print_exc()
            return None


# Global instance - will be initialised with API key from database
hardcover_service = HardcoverService()

